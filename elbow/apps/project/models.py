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
from elbow.apps.document.apps import DOCUMENT_TYPES

from .apps import PROJECT_STATUS, USE_PAYMENTOPTIONS, INTEREST_TYPE
from .managers import ProjectManager

import os
import datetime


def _image_upload_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return 'project/%s/img-%s%s' % (slugify(instance.slug), slugify(filename), file_extension)


def _doc_upload_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return 'project/%s/doc-%s%s' % (slugify(instance.slug), slugify(filename), file_extension)


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
    maximum_investment = MoneyField(max_digits=10, decimal_places=2, default=None, default_currency='EUR', blank=True, null=True)

    interest_type = models.CharField(choices=INTEREST_TYPE.get_choices(),
                                     default=INTEREST_TYPE.a,
                                     max_length=64,
                                     db_index=True)

    interest_rate = models.DecimalField(default=6.0, max_digits=6, decimal_places=2)
    interest_term = models.CharField(max_length=24, help_text=_('Format: 12m, 36m, 3y, 7y'), blank=True, null=True)

    proposition = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    building_type = models.CharField(max_length=255, blank=True, null=True)
    building_status = models.CharField(max_length=255, blank=True, null=True)
    building_location = models.CharField(max_length=255, blank=True, null=True)

    lat_long = GeopositionField(default='51.1655111, 6.2737308')

    documents = models.ManyToManyField('document.Document')

    term_sheet_doc = models.FileField(verbose_name=_('Term Sheet'),
                                      upload_to=_doc_upload_path,
                                      null=True,
                                      blank=True,
                                      storage=CustomManagedStorage())

    loan_agreement_doc = models.FileField(verbose_name=_('Loan Agreement'),
                                          upload_to=_doc_upload_path,
                                          max_length=255,
                                          null=True,
                                          blank=True,
                                          storage=CustomManagedStorage())

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

    redirect_url = models.URLField(verbose_name=_('Redirect URL'),
                                   help_text=_('If present the detail page will redirect here'),
                                   blank=True,
                                   null=True)

    date_available = models.DateField(blank=True, null=True)
    expiration = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProjectManager()

    class Meta:
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})

    @property
    def invest_now_url(self):
        return reverse('order:create', kwargs={'project_slug': self.slug})

    @property
    def running_time(self):
        return '?'

    @property
    def is_available_for_investment(self):
        return datetime.datetime.combine(self.date_available, datetime.time(0, 0)) <= datetime.datetime.today() if self.date_available else True

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

    @property
    def term_sheet_doc_permalink(self):
        return reverse('project:media_permalink', kwargs={'slug': self.slug, 'media_slug': 'term-sheet'}) if self.term_sheet_doc else None

    @property
    def loan_agreement_doc_permalink(self):
        return reverse('project:media_permalink', kwargs={'slug': self.slug, 'media_slug': 'loan-agreement'}) if self.loan_agreement_doc else None
