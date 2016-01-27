# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from elbow.utils import get_namedtuple_choices

from .handlers import post_save_send_payment_request


ORDER_STATUS = get_namedtuple_choices('ORDER_STATUS', (
    ('pending', 'pending', _('Pending')),
    ('processing', 'processing', _('Send for Processing')),
    ('paid', 'paid', _('Paid')),
    ('failed', 'failed', _('Payment Failed')),
    ('cancelled', 'cancelled', _('Payment Cancelled')),
))


class OrderConfig(AppConfig):
    name = 'order'

    def ready(self):
        post_save.connect(post_save_send_payment_request,
                          dispatch_uid="order.post_save_send_payment_request")
