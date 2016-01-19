# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # Projects
    url(r'^projects/', include('elbow.apps.project.urls', namespace='project')),
    # Orders
    url(r'^orders/', include('elbow.apps.order.urls', namespace='order')),
    # Paymill
    url(r'^paymill/', include('dj_paymill.urls', namespace='paymill')),
    # User Auth
    url(r'^auth/token/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^auth/token/refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('elbow.apps.public.urls', namespace='public')),
]

if settings.DEBUG is True:
    urlpatterns += staticfiles_urlpatterns()
