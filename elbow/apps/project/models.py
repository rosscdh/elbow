# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from autoslug import AutoSlugField
from embed_video.fields import EmbedVideoField
from elbow.utils import CustomManagedStorage

from .apps import PROJECT_STATUS, USE_PAYMENTOPTIONS


def _image_upload_path(cls, instance, filename):
    return 'project/%s-%s' % (instance.slug, slugify(filename))


class Project(models.Model):
    """
    Base Project that can be invested in
    """
    PROJECT_STATUS = PROJECT_STATUS
    USE_PAYMENTOPTIONS = USE_PAYMENTOPTIONS

    slug = AutoSlugField(populate_from='name')
    name = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=8, decimal_places=2)

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

    @property
    def url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})

    @property
    def num_backers(self):
        return self.order_set.all().count()

    @property
    def percent(self):
        return (float(self.revenue) / float(self.amount)) * 100

    @property
    def revenue(self):
        amount = self.order_set.all().annotate(sum=models.Sum('amount')).aggregate(models.Sum('sum')).get('sum__sum')
        return amount if amount else 0

