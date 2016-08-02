# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from elbow.utils import get_namedtuple_choices


ORDER_STATUS = get_namedtuple_choices('ORDER_STATUS', (
    ('created', 'created', _('Order Created (1/3)')),
    ('loan_agreement', 'loan_agreement', _('Loan Agreement (2/3)')),
    ('processing', 'processing', _('Processing Payment  (3/3)')),
    ('paid', 'paid', _('Paid')),
    ('paid_manually', 'paid_manually', _('Manually Paid')),
    ('failed', 'failed', _('Payment Failed')),
    ('cancelled', 'cancelled', _('Payment Cancelled')),
))

ORDER_PAYMENT_TYPE = get_namedtuple_choices('ORDER_PAYMENT_TYPE', (
    #('creditcard', 'creditcard', _('Credit card')),  # We dont support credit-cards transactions
    ('debit', 'debit', _('Bank debit')),
    ('prepay', 'prepay', _('Manual bank transfer')),
))

SECUPAY_BANK_DATA = {
    "bankcode": "30050000",
    "accountowner": "secupay AG",
    "bankname": "Landesbank Hessen-Th\\u00fcringen Girozentrale NL. D\\u00fcsseldorf",
    "iban": "DE93 3005 0000 7060 5077 33",
    "bic": "WELADEDDXXX",
    "accountnumber": "1747013"
}


class OrderConfig(AppConfig):
    name = 'elbow.apps.order'
