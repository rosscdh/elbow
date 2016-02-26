# -*- coding: UTF-8 -*-
from .services import SendEmailService

import logging
logger = logging.getLogger('django.request')


def send_admin_user_signup_email(*args, **kwargs):
    user = kwargs.pop('user', None)

    if user is not None:
        logger.info('Sending User signed up admin notification email')
        SendEmailService.send_user_signedup_admin_email(user_list=[user])
