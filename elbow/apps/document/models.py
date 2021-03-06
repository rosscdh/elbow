# -*- coding: UTF-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify

from elbow.utils import CustomManagedStorage

from shortuuidfield import ShortUUIDField

from .apps import DOCUMENT_STATUS, DOCUMENT_TYPES

import os


def _document_upload_path(instance, filename):
    filename, file_extension = os.path.splitext(filename)
    return 'document/%s%s' % (slugify(filename), file_extension)


class Document(models.Model):

    DOCUMENT_STATUS = DOCUMENT_STATUS
    DOCUMENT_TYPES = DOCUMENT_TYPES

    uuid = ShortUUIDField(db_index=True, blank=False)

    user = models.ForeignKey('auth.User', blank=True, null=True)

    name = models.CharField(max_length=128)

    document = models.FileField(upload_to=_document_upload_path,
                                storage=CustomManagedStorage(),
                                max_length=255,
                                blank=True, null=True)

    document_type = models.CharField(choices=DOCUMENT_TYPES.get_choices(),
                                     default=DOCUMENT_TYPES.project,
                                     max_length=64,
                                     db_index=True)

    status = models.CharField(choices=DOCUMENT_STATUS.get_choices(),
                              default=DOCUMENT_STATUS.active,
                              max_length=64,
                              db_index=True)

    login_required = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    @property
    def url(self):
        url_kwargs = {'uuid': self.uuid}
        return reverse('document:download', kwargs=url_kwargs)
