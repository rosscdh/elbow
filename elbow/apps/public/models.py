# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models

from jsonfield import JSONField


class UserProfile(models.Model):
    user = models.OneToOneField('auth.User')
    data = JSONField(default={})
