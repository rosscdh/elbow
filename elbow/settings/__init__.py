"""
Django settings for m1_news project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_ENVIRONMENT = DJANGO_ENV = os.getenv('DJANGO_ENV', os.getenv('RAILS_ENV', 'development'))

ROLLBAR_POST_SERVER_ITEM_ACCESS_TOKEN = None

#
# Load common settings
#
from .common_settings import *

#
# Load the environment specific settings
#
try:
    environment_settings = open(os.path.join(BASE_DIR, '../', 'config/environments/{DJANGO_ENV}/elbow/local_settings.py'.format(DJANGO_ENV=DJANGO_ENV)))
    exec(environment_settings)
except Exception as e:
    pass

#
# Load specific local_settings.py settings in case we want to override something for an env
#
try:
    from ..local_settings import *
except ImportError:
    # no local_settings.py found
    pass

#
# Comes last
#
from .logging_settings import *

#
# Check for test settings
#
for test_app in ['testserver', 'test', 'jenkins']:
    if test_app in sys.argv[1:2]:
        PROJECT_ENVIRONMENT = 'test'
        from test_settings import *
