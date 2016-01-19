# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import ListView, DetailView

from .models import Project

urlpatterns = patterns('',
                       url(r'^$',
                           ListView.as_view(template_name='project/project-list.html',
                                            model=Project),
                           name='list'),

                       url(r'^(?P<slug>[\w-]+)/$',
                           DetailView.as_view(template_name='project/project-detail.html',
                                              model=Project),
                           name='detail'),)
