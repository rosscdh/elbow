# -*- coding: UTF-8 -*-
from __future__ import unicode_literals
from django.db import models


class ProjectManager(models.Manager):
    def public(self, **kwargs):
        return self.get_queryset().filter(status__in=[self.model.PROJECT_STATUS.active,  \
                                                      self.model.PROJECT_STATUS.complete])  \
                                  .filter(**kwargs)
