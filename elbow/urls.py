# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # Projects
    url(r'^projects/', include('elbow.apps.project.urls', namespace='project')),

    # User Auth
    url(r'^auth/token/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^auth/token/refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),
    url(r'^auth/', include('rest_auth.urls')),
    url(r'^auth/registration/', include('rest_auth.registration.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^', include('django.contrib.auth.urls')),
]

if settings.DEBUG is True:
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
