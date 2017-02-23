# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import url, include
from django.conf.urls.i18n import i18n_patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.decorators.cache import never_cache

from elbow.apps.public.views import LoginView, SignupView

urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^api/v1/', include('elbow.apps.api.urls', namespace='api')),

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
    url(r'^accounts/login/', never_cache(LoginView.as_view()), name='account_login'),
    url(r'^accounts/signup/', never_cache(SignupView.as_view()), name='account_signup'),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^', include('elbow.apps.public.urls', namespace='public')),
    url(r'^p/', include('pages.urls')), # check public/urls.py
    url(r'^robots\.txt$', include('robots.urls')),
    url(r'^', include('django.contrib.auth.urls')),

) + staticfiles_urlpatterns() + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
