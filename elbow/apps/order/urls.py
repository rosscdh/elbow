# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import OrderCreate, OrderPayment, OrderDetail

urlpatterns = patterns('',
                       url(r'^(?P<project_slug>[\w-]+)/order/$',
                           OrderCreate.as_view(),
                           name='create'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>.*)/$',
                           OrderPayment.as_view(),
                           name='payment'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<slug>[\w-]+)/$',
                           OrderDetail.as_view(),
                           name='detail'),)
