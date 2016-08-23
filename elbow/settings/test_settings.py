# -*- coding: utf-8 -*-
LOCAL_SETTINGS = True

from . import BASE_DIR

import os
import logging

logging.disable(logging.CRITICAL)

DEBUG = False  # msut be set to false to emulate production

TEST_RUNNER = 'elbow.tests.test_runner.AppTestRunner'

PROJECT_ENVIRONMENT = 'test'

ATOMIC_REQUESTS = True

#
# For the moment we use sqlite3 for testing as we are not doign anything postgres specific
#
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'dev.db'),
    }
}

# faster passwords but far less secure in test
PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.MD5PasswordHasher',
)

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

PROCESS_IMAGES_ASYNC = False

STATIC_ROOT = os.path.join(BASE_DIR, '../', 'static')
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, '../', 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


BASE_URL = 'http://localhost:8009'
