# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import (DocumentDownload,)

urlpatterns = patterns('',
                       url(r'^(?P<uuid>[\w-]+)/download/$',
                           DocumentDownload.as_view(),
                           name='download'),)
