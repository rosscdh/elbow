# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.generic import TemplateView, ListView

from .models import Project
from .views import ProjectDetailView, PDFPermalinkView


urlpatterns = patterns('',
                       url(r'^project-api/$', TemplateView.as_view(template_name='project/api-project-list.html')),
                       url(r'^$',
                           ListView.as_view(template_name='project/project-list.html',
                                            model=Project,
                                            queryset=Project.objects.public()),
                           name='list'),

                       url(r'^(?P<slug>[\w-]+)/media/(?P<media_slug>[\w-]+)/permalink/$',
                           PDFPermalinkView.as_view(),
                           name='media_permalink'),

                       url(r'^(?P<slug>[\w-]+)/$',
                           ProjectDetailView.as_view(),
                           name='detail'),)
