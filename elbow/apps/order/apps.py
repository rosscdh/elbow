# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.dispatch import receiver
from django.db.models.signals import post_save

from elbow.utils import get_namedtuple_choices

from .handlers import post_save_send_payment_request


ORDER_STATUS = get_namedtuple_choices('ORDER_STATUS', (
    ('pending', 'pending', 'Pending'),
    ('new', 'new', 'New'),
    ('processing', 'processing', 'Send for Processing'),
    ('paid', 'paid', 'Paid'),
    ('canceled', 'canceled', 'Canceled'),
))


class OrderConfig(AppConfig):
    name = 'order'

    def ready(self):
        post_save.connect(post_save_send_payment_request,
                          dispatch_uid="order.post_save_send_payment_request")
