# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.conf import settings
from django.template import loader
from django.core.urlresolvers import reverse
from django.utils.translation import activate
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from secupay import SecuPay
from jsonfield import JSONField
from pinax.eventlog.models import log
from djmoney.models.fields import MoneyField

from .apps import ORDER_STATUS, ORDER_PAYMENT_TYPE, SECUPAY_BANK_DATA
from .managers import OrderManager

from shortuuidfield import ShortUUIDField

import re
import logging
logger = logging.getLogger('django.request')


class Order(models.Model):
    BASE_URL = getattr(settings, 'BASE_URL', 'http://localhost:8009')

    ORDER_STATUS = ORDER_STATUS
    ORDER_PAYMENT_TYPE = ORDER_PAYMENT_TYPE

    SECUPAY = SecuPay(settings=settings)
    SECUPAY_BANK_DATA = SECUPAY_BANK_DATA

    uuid = ShortUUIDField(db_index=True)
    user = models.ForeignKey('auth.User')
    project = models.ForeignKey('project.Project')
    payment_option = models.ForeignKey('order.PaymentOption', blank=True, null=True)

    transaction_id = models.CharField(max_length=128, blank=True, null=True)

    title = models.CharField(max_length=24, blank=True, null=True)
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    dob = models.DateField(auto_now=False, auto_now_add=False, blank=True, null=True)

    address_1 = models.CharField(max_length=255, blank=True, null=True)
    address_2 = models.CharField(max_length=255, blank=True, null=True)
    postcode = models.CharField(max_length=24, blank=True, null=True)
    city = models.CharField(max_length=24, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)

    status = models.CharField(choices=ORDER_STATUS.get_choices(),
                              default=ORDER_STATUS.created,
                              max_length=64,
                              db_index=True)

    payment_type = models.CharField(choices=ORDER_PAYMENT_TYPE.get_choices(),
                                    default=ORDER_PAYMENT_TYPE.debit,
                                    max_length=24,
                                    db_index=True)

    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    shipping = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tracking_number = models.CharField(max_length=128, blank=True, null=True)

    data = JSONField(default={})

    expiration = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    documents = models.ManyToManyField('document.Document')

    objects = OrderManager()

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ('-created_at',)

    @property
    def display_payment_type(self):
        return self.ORDER_PAYMENT_TYPE.get_desc_by_value(self.payment_type)

    @property
    def url(self):
        """
        Basic State-Machine need to integrate
        """
        url_kwargs = {'project_slug': self.project.slug, 'uuid': self.uuid}

        if self.status in [self.ORDER_STATUS.paid, self.ORDER_STATUS.processing]:
            return reverse('order:detail', kwargs=url_kwargs)

        if self.status == self.ORDER_STATUS.created:
            #
            # Has completed primary step but may need to agree to
            # large sum agreement, either way they must ahve the opportunity
            # to download the load agreement or not
            #
            return reverse('order:loan_agreement', kwargs=url_kwargs)

        if self.status == self.ORDER_STATUS.loan_agreement:
            #
            # Completed the steps but needs to pay
            #
            return reverse('order:payment', kwargs=url_kwargs)
        #
        # Default out to show order detail page
        #
        return reverse('order:detail', kwargs=url_kwargs)

    @property
    def is_large_amount(self):
        """
        In order to be sent to secupay, we must be in "processing" status AND have a None for transaction_id
        """
        return self.amount.amount >= 1000

    @property
    def can_send_payment(self):
        """
        In order to be sent to secupay, we must be in "processing" status AND have a None for transaction_id
        """
        return self.status in [self.ORDER_STATUS.processing] and self.transaction_id in [None, '']

    @property
    def can_continue_process(self):
        """
        If the user has not completed their investment process allow them to continue via this check
        """
        return self.status in [self.ORDER_STATUS.created,
                               self.ORDER_STATUS.loan_agreement] and self.transaction_id in [None, '']

    @property
    def content_type(self):
        return ContentType.objects.filter(app_label='order', model='order').first()

    @property
    def log_history(self):
        return self.content_type.log_set.filter(object_id=self.pk)

    @property
    def url_success(self):
        activate(settings.LANGUAGE_CODE)
        return '%s%s' % (self.BASE_URL, reverse('order:payment_success', kwargs={'project_slug': self.project.slug, 'uuid': self.uuid}))

    @property
    def url_failure(self):
        activate(settings.LANGUAGE_CODE)
        return '%s%s' % (self.BASE_URL, reverse('order:payment_failure', kwargs={'project_slug': self.project.slug, 'uuid': self.uuid}))

    @property
    def url_webhook(self):
        activate(settings.LANGUAGE_CODE)
        return '%s%s' % (self.BASE_URL, reverse('order:payment_webhook', kwargs={'project_slug': self.project.slug, 'uuid': self.uuid}))

    @property
    def address(self):
        return loader.render_to_string('order/_address.html', {
                'address_1': self.address_1,
                'address_2': self.address_2,
                'postcode': self.postcode,
                'city': self.city,
                'country': self.country,
        })

    def __unicode__(self):
        return '%s - %s (%s)' % (self.amount, self.transaction_id, self.payment_type)

    def make_payment(self, user):
        """
        Primary make payment interface returns the iframe url
        """
        resp = {}

        amount = str(self.amount.amount)
        logger.info('make_payment: {order} {amount} {type}'.format(order=self,
                                                                   amount=amount,
                                                                   type=self.payment_type))

        secupay_required_values = {
            "purpose": 'TodayCapital-%d' % self.pk,  # Shown to user on bank statement
            "firstname": self.customer_name.split(' ')[0],
            "lastname": ' '.join(self.customer_name.split(' ')[1:]),
            "street": self.address_1,
            "housenumber": self.address_2,
            "zip": self.postcode,
            "city": self.city,
            "country": self.country,
            "email": self.user.email,
        }

        resp = self.SECUPAY.payment().make_payment(amount=amount,
                                                   payment_type=self.payment_type,
                                                   url_success=self.url_success,
                                                   url_failure=self.url_failure,
                                                   url_push=self.url_webhook,
                                                   **secupay_required_values)

        log(
            user=user,
            action="order.lifecycle.payment.make_payment",
            obj=self,
            extra=resp
        )

        self.transaction_id = resp.get('data', {}).get('hash')

        self.tracking_number = resp.get('data', {}).get('purpose')
        #
        # @NOTE Secupay limitation
        # Will happen in the case of direct debit, no purpose will be provided.
        # thus we need to use their hash as a relatively simple code as requested by TC
        #
        if self.tracking_number is None:
            #
            # where hash is upptaaluefxm967881
            # (Pdb) match.groups()
            # (u'upptaaluefxm', u'967881')
            #
            match = re.search('^([a-zA-Z]+)(\d+)$', self.transaction_id)
            self.tracking_number = 'TA %s' % match.group(2)

        # Replace the TA- with TH- as requestd by client
        # we save the original TA-***** number in the order.data json
        if self.tracking_number is not None:
            self.tracking_number = self.tracking_number.replace('TA ', 'TC-')

        self.data = resp.get('data', {})
        self.save(update_fields=['transaction_id', 'tracking_number', 'data'])

        return self, resp

    def capture_authorized_payment(self, user):
        resp = self.SECUPAY.payment().capture_preauthorized_payment(token=self.transaction_id)

        log(
            user=user,
            action="order.lifecycle.payment.capture_authorized_payment",
            obj=self,
            extra=resp
        )
        data = resp.get('data', {})
        self.data['capture'] = data

        if data.get('status') == 'ok':
            self.status = self.ORDER_STATUS.paid

        self.save(update_fields=['status', 'data'])

        return self, resp


class PaymentOption(models.Model):
    project = models.ForeignKey('project.Project', blank=True, null=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField()
    shipping_desc = models.CharField(max_length=255, blank=True, null=True)
    delivery_desc = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
