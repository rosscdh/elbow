# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models


class OrderManager(models.Manager):
    def paid(self, **kwargs):
        return self.get_queryset().filter(status__in=[self.model.ORDER_STATUS.paid]).filter(**kwargs)
