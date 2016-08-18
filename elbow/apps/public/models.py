# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models

from jsonfield import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User')

    #
    # Field used to provider filter capabilities in the admin system
    # is a indexable searchable and a "duplicate" of the value stored
    # in json data field
    #
    send_news_and_info = models.NullBooleanField(db_index=True)

    data = JSONField(default={})
