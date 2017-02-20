# -*- coding: UTF-8 -*-
from . import BASE_DIR

try:
    from ..local_settings import PROJECT_ENVIRONMENT
    from ..local_settings import ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN
except Exception as e:
    from . import PROJECT_ENVIRONMENT
    from . import ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN

import os
import datetime

DJANGO_ENV = os.getenv('DJANGO_ENV', os.getenv('RAILS_ENV', 'development'))

SITE_ID = 1

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '2=il^vfe7b_(q&qloc5mzju$l=#-8%*@__%=5yhah0obaie!^_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ADMINS = [
    'sendrossemail+elbow@gmail.com'
]

MANAGERS = ADMINS

DEFAULT_FROM_EMAIL = SERVER_EMAIL = 'post@todaycapital.de'

ALLOWED_HOSTS = ['*']

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Application definition
DJANGO_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
)

PROJECT_APPS = (
    'elbow.apps.api',
    'elbow.apps.public',
    'elbow.apps.project',
    'elbow.apps.document',
    'elbow.apps.order',
)

HELPER_APPS = (
    'pipeline',
    'djangobower',
    'crispy_forms',
    'django_extensions',

    # 'corsheaders',
    # 'rest_framework',
    # 'rest_framework.authtoken',
    # 'rest_framework_swagger',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rest_auth',

    'robots',

    'pinax.eventlog',

    'geoposition',
    'leaflet',

    'corsheaders',
    'rest_framework',

    'import_export',

    'pages', # cms
    'taggit', # cms
    'mptt',  # for cms
    'rulez',
    'djmoney',
    'embed_video',
    'django_inlinecss',
    #  'django_rq',
    'easy_thumbnails',
    'easy_pdf',
)

INSTALLED_APPS = DJANGO_APPS + PROJECT_APPS + HELPER_APPS

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware', # Not required as we load allot from 3rd party sites in iframe
    # Language
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    # Minify
    'pipeline.middleware.MinifyHTMLMiddleware',
    # must come last
    'rollbar.contrib.django.middleware.RollbarNotifierMiddleware',
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'djangobower.finders.BowerFinder',
    'pipeline.finders.PipelineFinder',
    'pipeline.finders.ManifestFinder',
)

STATICFILES_STORAGE = 'pipeline.storage.PipelineStorage'

ROBOTS_USE_SITEMAP = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, '../', 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, '../', 'media')
MEDIA_URL = '/media/'

ROOT_URLCONF = 'elbow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.template.context_processors.debug",
                'django.template.context_processors.request',
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "pages.context_processors.media",
                "elbow.context_processors.elbow_globals",
            ],
        },
    },
]

WSGI_APPLICATION = 'elbow.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

ROLLBAR = {
    'access_token': ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN,
    'environment': PROJECT_ENVIRONMENT,
    'branch': 'master',
    'root': BASE_DIR,
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = ('*',)
# CORS_ALLOW_HEADERS = (
#     'x-requested-with',
#     'content-type',
#     'accept',
#     'origin',
#     'authorization',
#     'x-csrftoken'
# )

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        # 'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
        #'elbow.apps.api.permissions.ApiObjectPermission',
    ),
    'DEFAULT_MODEL_SERIALIZER_CLASS':
        'rest_framework.serializers.ModelSerializer',

    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework.filters.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 30,
    'DEFAULT_CACHE_RESPONSE_TIMEOUT': 60 * 5,
}

JWT_AUTH = {
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'JWT_ALLOW_REFRESH': False,
    'JWT_VERIFY_EXPIRATION': False,
    'JWT_LEEWAY': 300,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(seconds=300),
    'JWT_REFRESH_EXPIRATION_DELTA': datetime.timedelta(days=7),
}

AUTHENTICATION_BACKENDS = (
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
    'rulez.backends.ObjectPermissionBackend',
)

# All Auth /rest-auth config
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = 'https://today-capital.de'
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = 'https://today-capital.de'
ACCOUNT_LOGOUT_ON_GET = True
LOGIN_REDIRECT_URL = '/de/projects/todayhaus/'

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, '../')

BOWER_INSTALLED_APPS = (
    "bootstrap-sass#3.3.6",
    'famfamfam-flags#0.5.0',
    'moment#2.9.0',
    'accruejs#0.0.1',
)

CRISPY_TEMPLATE_PACK = 'bootstrap3'


MOMMY_CUSTOM_FIELDS_GEN = {
    'autoslug.fields.AutoSlugField': lambda: None
}

PAYMILL = {
    'PRIVATE_API_KEY': 'd1269f85bd99db07d3c7437c8a435047',
    'WEBHOOK_URI': 'http://example.com/',
}

DEFAULT_CURRENCY = 'EUR'
DEFAULT_CURRENCY_SYMBOL = '€'

CRISPY_FAIL_SILENTLY = False

ACCOUNT_FORMS = {
    'signup': 'elbow.apps.public.forms.SignUpForm',
}

# CMS settings
PAGE_CONTENT_REVISION = False  # Dont keep revisions
PAGE_TAGGING = True  # Allow for footer and page tagging
PAGE_CONTENT_REVISION_DEPTH = 1
PAGE_DEFAULT_TEMPLATE = 'pages/70_30.html'
PAGE_TEMPLATES = (
    ('pages/home_page.html', 'Homepage'),
    ('pages/70_40.html', '70/30'),
)

# This is defined here as a do-nothing function because we can't import
# django.utils.translation -- that module depends on the settings.
gettext_noop = lambda s: s

PAGE_LANGUAGES = LANGUAGES = (
    ('de', gettext_noop('German')),
    # ('en-gb', gettext_noop('English')),
)

# copy PAGE_LANGUAGES
languages = list(PAGE_LANGUAGES)

# redefine the LANGUAGES setting in order to be sure to have the correct request.LANGUAGE_CODE
LANGUAGES = languages

SECUPAY_TOKEN = 'testToken'
SECUPAY_DEVELOPMENT = True
SECUPAY_DEMO = True

SECUPAY_LABELS = {
    "en_US": {
        "basket_title": "Your Order",
        "submit_button_title": "Submit",
        "cancel_button_title": "Return to Project"
    },
    "de_DE": {
        "basket_title": "Ihre Bestellung",
        "submit_button_title": "Daten Ubermitteln",
        "cancel_button_title": u"Zurück zum Projekt"
    }
}

LOCALE_PATHS = [
    os.path.join(BASE_DIR, '../', 'locale')
]

LEAFLET_CONFIG = {
    'DEFAULT_CENTER': (51.1655111, 6.2737308),
    'DEFAULT_ZOOM': 12,
    'MIN_ZOOM': 12,
    # 'MAX_ZOOM': 18,
}


TERMS_AND_CONDITIONS_URL = 'https://today-capital.de/impressum/agb/'

#
# All auth
#


def _user_display(user):
    if user.first_name and user.last_name:
        return u'%s %s' % (user.first_name, user.last_name)
    if user.first_name:
        return u'%s' % (user.first_name,)
    return user.email

ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ''
ACCOUNT_USER_DISPLAY = _user_display
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
