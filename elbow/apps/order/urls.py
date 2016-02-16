# -*- coding: utf-8 -*-
from django.conf.urls import patterns, url
from django.views.decorators.csrf import csrf_exempt

from .views import (OrderCreate,
                    OrderLoanAgreementView,
                    OrderPayment,
                    UserOrderList,
                    OrderDetail,
                    OrderWebhook)

urlpatterns = patterns('',
                       url(r'^$',
                           UserOrderList.as_view(),
                           name='user_list'),

                       url(r'^(?P<project_slug>[\w-]+)/order/$',
                           OrderCreate.as_view(),
                           name='create'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/loan-agreement/$',
                           OrderLoanAgreementView.as_view(),
                           name='loan_agreement'),

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
                           OrderDetail.as_view(template_name='order/order-payment_success.html'),
                           name='payment_success'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/failure/$',
                           OrderDetail.as_view(template_name='order/order-payment_failed.html'),
                           name='payment_failure'),

                       url(r'^(?P<project_slug>[\w-]+)/order/(?P<uuid>[\w-]+)/payment/webhook/$',
                           csrf_exempt(OrderWebhook.as_view()),
                           name='payment_webhook'),)
