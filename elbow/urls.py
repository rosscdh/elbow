# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    # Projects
    url(r'^projects/', include('elbow.apps.project.urls', namespace='project')),
    # Orders
    url(r'^orders/', include('elbow.apps.order.urls', namespace='order')),
    # Documents
    url(r'^documents/', include('elbow.apps.document.urls', namespace='document')),
    # Paymill
    # url(r'^paymill/', include('dj_paymill.urls', namespace='paymill')),
    # User Auth
    # url(r'^auth/token/', 'rest_framework_jwt.views.obtain_jwt_token'),
    # url(r'^auth/token/refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),
    # url(r'^auth/', include('rest_auth.urls')),
    # url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^p/', include('pages.urls')),
    url(r'^', include('django.contrib.auth.urls')),
    url(r'^', include('elbow.apps.public.urls', namespace='public')),
) + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
