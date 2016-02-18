# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from moneyed import Money

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.contrib.contenttypes.models import ContentType

from djmoney.models.fields import MoneyField
from geoposition.fields import GeopositionField

from autoslug import AutoSlugField
from embed_video.fields import EmbedVideoField
from elbow.utils import CustomManagedStorage

from .apps import PROJECT_STATUS, USE_PAYMENTOPTIONS, INTEREST_TYPE
from .managers import ProjectManager

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
    INTEREST_TYPE = INTEREST_TYPE

    slug = AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)

    amount = MoneyField(max_digits=10, decimal_places=2, default_currency='EUR')
    minimum_investment = MoneyField(max_digits=10, decimal_places=2, default=500, default_currency='EUR')
    interest_type = models.CharField(choices=INTEREST_TYPE.get_choices(),
                                     default=INTEREST_TYPE.a,
                                     max_length=64,
                                     db_index=True)

    interest_rate = models.IntegerField(default=6.0)
    interest_length = models.CharField(max_length=24, blank=True, null=True)

    proposition = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    building_type = models.CharField(max_length=255, blank=True, null=True)
    building_status = models.CharField(max_length=255, blank=True, null=True)
    building_location = models.CharField(max_length=255, blank=True, null=True)

    lat_long = GeopositionField(default=(51.1655111, 6.2737308))

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

    objects = ProjectManager()

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
        return self.order_set.paid().count()

    @property
    def percent(self):
        if self.amount.amount > 0:
            return (float(self.revenue.amount) / float(self.amount.amount)) * 100
        else:
            return 0

    @property
    def revenue(self):
        amount = self.order_set.paid().annotate(sum=models.Sum('amount')).aggregate(models.Sum('sum')).get('sum__sum')
        return Money(amount, 'EUR') if amount else Money(0, 'EUR')

    @property
    def content_type(self):
        return ContentType.objects.filter(app_label='project', model='project').first()

    @property
    def news_history(self):
        return self.content_type.log_set.filter(object_id=self.pk)
