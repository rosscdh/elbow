# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.db import models
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

    phone = models.CharField(max_length=128, blank=True, null=True)

    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
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
    def url(self):
        """
        Basic State-Machine need to integrate
        """
        url_kwargs = {'project_slug': self.project.slug, 'uuid': self.uuid}

        if self.status in [self.ORDER_STATUS.paid, self.ORDER_STATUS.processing]:
            return reverse('order:detail', kwargs=url_kwargs)

        if self.status == self.ORDER_STATUS.created:
            #
            # Has only completed step 1 needs to complete the rest
            #
            return reverse('order:more_info', kwargs=url_kwargs)

        if self.status == self.ORDER_STATUS.more_info:
            #
            # Has completed more info step but needs to agree to large sum agreement
            #
            if self.amount.amount <= 1000:
                return reverse('order:payment', kwargs=url_kwargs)
            else:
                return reverse('order:large_sum_agreement', kwargs=url_kwargs)

        if self.status == self.ORDER_STATUS.large_sum_agreement:
            #
            # Completed the steps but needs to pay
            #
            return reverse('order:payment', kwargs=url_kwargs)
        #
        # Default out to show order detail page
        #
        return reverse('order:detail', kwargs=url_kwargs)

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
                               self.ORDER_STATUS.large_sum_agreement,
                               self.ORDER_STATUS.more_info,] and self.transaction_id in [None, '']

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
        resp = self.SECUPAY.payment().make_payment(amount=amount,
                                                   payment_type=self.payment_type,
                                                   url_success=self.url_success,
                                                   url_failure=self.url_failure,
                                                   url_push=self.url_webhook)
        log(
            user=user,
            action="order.lifecycle.payment.make_payment",
            obj=self,
            extra=resp
        )

        self.transaction_id = resp.get('data', {}).get('hash')
        self.data = resp.get('data', {})
        self.save(update_fields=['transaction_id', 'data'])

        return self, resp

    def capture_authorized_payment(self, user):
        resp = self.SECUPAY.payment().capture_preauthorized_payment(token=self.transaction_id)

        log(
            user=user,
            action="order.lifecycle.payment.capture_authorized_payment",
            obj=self,
            extra=resp
        )

        self.data['capture'] = resp.get('data', {})
        self.save(update_fields=['data'])

        return self, resp


class PaymentOption(models.Model):
    project = models.ForeignKey('project.Project', blank=True, null=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField()
    shipping_desc = models.CharField(max_length=255, blank=True, null=True)
    delivery_desc = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
