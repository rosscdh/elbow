# -*- coding: utf-8 -*-
from django.conf import settings


def elbow_globals(request):
    return {
        'SECUPAY_DEMO': getattr(settings, 'SECUPAY_DEMO', False),
        'BASE_URL': getattr(settings, 'BASE_URL', None),
    }
