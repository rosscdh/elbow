# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.template.defaultfilters import slugify

from elbow.utils import CustomManagedStorage

from shortuuidfield import ShortUUIDField

from .apps import DOCUMENT_STATUS


def _document_upload_path(cls, instance, filename):
    return 'document/%s-%s' % (instance.uuid, slugify(filename))


class Document(models.Model):
    DOCUMENT_STATUS = DOCUMENT_STATUS

    uuid = ShortUUIDField(db_index=True, blank=False)

    name = models.CharField(max_length=128)

    document = models.FileField(upload_to=_document_upload_path,
                                storage=CustomManagedStorage(),
                                blank=True, null=True)

    status = models.CharField(choices=DOCUMENT_STATUS.get_choices(),
                              default=DOCUMENT_STATUS.active,
                              max_length=64,
                              db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
