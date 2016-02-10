# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from elbow.utils import get_namedtuple_choices

from .handlers import post_save_send_payment_request


ORDER_STATUS = get_namedtuple_choices('ORDER_STATUS', (
    ('created', 'created', _('Order Created (1/4)')),
    ('large_sum_agreement', 'large_sum_agreement', _('Large sum agreement (2/4)')),
    ('more_info', 'more_info', _('More Info (3/4)')),
    ('processing', 'processing', _('Send for Payment  (4/4)')),
    ('paid', 'paid', _('Paid')),
    ('paid_manually', 'paid_manually', _('Manually Paid')),
    ('failed', 'failed', _('Payment Failed')),
    ('cancelled', 'cancelled', _('Payment Cancelled')),
))

ORDER_PAYMENT_TYPE = get_namedtuple_choices('ORDER_PAYMENT_TYPE', (
    ('prepay', 'prepay', _('Manual bank transfer')),
    #('creditcard', 'creditcard', _('Credit card')),  # We dont support credit-cards transactions
    ('debit', 'debit', _('Bank debit')),
))

SECUPAY_BANK_DATA = {
  "bankcode": "30050000",
  "accountowner": "secupay AG",
  "iban": "DE88300500000001747013",
  "bic": "WELADEDDXXX",
  "accountnumber": "1747013"
}


class OrderConfig(AppConfig):
    name = 'order'

    def ready(self):
        post_save.connect(post_save_send_payment_request,
                          dispatch_uid="order.post_save_send_payment_request")
