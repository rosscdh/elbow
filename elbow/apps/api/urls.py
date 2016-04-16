# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from elbow.apps.project.api.views import ProjectListAPIView

#
# Standard URLS
#
urlpatterns = [
    # Projects
    url(r'^projects/$', csrf_exempt(ProjectListAPIView.as_view()), name='projects'),
]
