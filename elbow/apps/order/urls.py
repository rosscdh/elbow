# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url

from .views import (OrderCreate,
                    OrderMoreInfo,
                    OrderLargeSumAgreement,
                    OrderPayment,
                    OrderDetail,
                    OrderWebhook)

urlpatterns = patterns('',
                       url(r'^(?P<project_slug>[\w-]+)/order/$',
                           OrderCreate.as_view(),
                           name='create'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/more-info/$',
                           OrderMoreInfo.as_view(),
                           name='more_info'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/large-sum-agreement/$',
                           OrderLargeSumAgreement.as_view(),
                           name='large_sum_agreement'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>.*)/payment/$',
                           OrderPayment.as_view(),
                           name='payment'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/$',
                           OrderDetail.as_view(),
                           name='detail'),

                       #
                       # Payment integration, All are webhooks
                       #
                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/successful/$',
                           OrderWebhook.as_view(),
                           name='payment_success'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/failure/$',
                           OrderWebhook.as_view(),
                           name='payment_failure'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/webhook/$',
                           OrderWebhook.as_view(),
                           name='payment_webhook'),)
