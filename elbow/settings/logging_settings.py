# -*- coding: utf-8 -*-
try:
    from ..local_settings import PROJECT_ENVIRONMENT
except Exception as e:
    from . import PROJECT_ENVIRONMENT


#
# Development
#
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
        'werkzeug': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        }
    }
}


if PROJECT_ENVIRONMENT in ['staging', 'production']:

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'verbose': {
                'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
            },
            'simple': {
                'format': '%(levelname)s %(message)s'
            },
            'papertrail_format': {
                'format': '%(asctime)s [%(levelname)s] [%(filename)s->%(funcName)s] %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'papertrail_handler': {
                'level': 'INFO',
                'class': 'logging.handlers.SysLogHandler',
                'address': ('logs4.papertrailapp.com', 16417),
                'formatter': 'papertrail_format',
            },
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'papertrail_format',
            }
        },
        'loggers': {
            'django.request': {
                'handlers': ['papertrail_handler'],
                'level': 'INFO',
            },
        }
    }
