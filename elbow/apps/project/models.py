# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from moneyed import Money

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from djmoney.models.fields import MoneyField

from autoslug import AutoSlugField
from embed_video.fields import EmbedVideoField
from elbow.utils import CustomManagedStorage

from .apps import PROJECT_STATUS, USE_PAYMENTOPTIONS

import os


def _image_upload_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return 'project/%s-%s.%s' % (instance.uuid, slugify(filename), file_extension)


class Project(models.Model):
    """
    Base Project that can be invested in
    """
    PROJECT_STATUS = PROJECT_STATUS
    USE_PAYMENTOPTIONS = USE_PAYMENTOPTIONS

    slug = AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)

    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')

    proposition = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    documents = models.ManyToManyField('document.Document')

    # Sent to payment processor as description
    payment_description = models.CharField(max_length=255, blank=True, null=True)
    use_payment_options = models.CharField(choices=USE_PAYMENTOPTIONS.get_choices(),
                                           default=USE_PAYMENTOPTIONS.no,
                                           max_length=3,
                                           db_index=True)

    image = models.ImageField(upload_to=_image_upload_path,
                              storage=CustomManagedStorage(),
                              blank=True, null=True)
    video = EmbedVideoField(blank=True, null=True)

    status = models.CharField(choices=PROJECT_STATUS.get_choices(),
                              default=PROJECT_STATUS.pending,
                              max_length=64,
                              db_index=True)

    expiration = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})

    @property
    def num_backers(self):
        return self.order_set.filter(status__in=['paid']).count()

    @property
    def percent(self):
        if self.amount.amount > 0:
            return (float(self.revenue.amount) / float(self.amount.amount)) * 100
        else:
            return 0

    @property
    def revenue(self):
        amount = self.order_set.filter(status__in=['paid']).annotate(sum=models.Sum('amount')).aggregate(models.Sum('sum')).get('sum__sum')
        return Money(amount, 'EUR') if amount else Money(0, 'EUR')

