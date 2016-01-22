# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.utils.translation import ugettext_lazy as _

from djmoney.models.fields import MoneyField

from .apps import ORDER_STATUS

from shortuuidfield import ShortUUIDField


class Order(models.Model):
    ORDER_STATUS = ORDER_STATUS

    uuid = ShortUUIDField(db_index=True)
    user = models.ForeignKey('auth.User')
    project = models.ForeignKey('project.Project')
    payment_option = models.ForeignKey('order.PaymentOption', blank=True, null=True)

    token = models.CharField(max_length=255, blank=True, null=True)
    transaction_id = models.CharField(max_length=128, blank=True, null=True)

    phone = models.CharField(max_length=128, blank=True, null=True)

    customer_name = models.CharField(max_length=255, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)

    status = models.CharField(choices=ORDER_STATUS.get_choices(),
                              default=ORDER_STATUS.pending,
                              max_length=64,
                              db_index=True)

    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    shipping = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    tracking_number = models.CharField(max_length=128, blank=True, null=True)

    expiration = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')


class PaymentOption(models.Model):
    project = models.ForeignKey('project.Project', blank=True, null=True)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

    description = models.TextField()
    shipping_desc = models.CharField(max_length=255, blank=True, null=True)
    delivery_desc = models.CharField(max_length=255, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
