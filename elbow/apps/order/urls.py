# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import OrderCreate, OrderPayment, OrderDetail

urlpatterns = patterns('',
                       url(r'^(?P<project_slug>[\w-]+)/order/$',
                           OrderCreate.as_view(),
                           name='create'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>.*)/payment/$',
                           OrderPayment.as_view(),
                           name='payment'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/$',
                           OrderDetail.as_view(),
                           name='detail'),

                       #
                       # Secupay integration
                       #
                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/successful/$',
                           OrderDetail.as_view(),
                           name='payment_success'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/failure/$',
                           OrderDetail.as_view(),
                           name='payment_failure'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/webhook/$',
                           OrderDetail.as_view(),
                           name='payment_webhook'),)
