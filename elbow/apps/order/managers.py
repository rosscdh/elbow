# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models


class OrderManager(models.Manager):
    def paid(self, **kwargs):
        return self.get_queryset().filter(status__in=[self.model.ORDER_STATUS.paid, self.model.ORDER_STATUS.paid_manually]).filter(**kwargs)

    def potential(self, **kwargs):
        return self.get_queryset().filter(status__in=[self.model.ORDER_STATUS.loan_agreement,
                                                      self.model.ORDER_STATUS.processing,
                                                      self.model.ORDER_STATUS.paid,
                                                      self.model.ORDER_STATUS.paid_manually,]).filter(**kwargs)
