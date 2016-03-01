# -*- coding: UTF-8 -*-
from .services import SendEmailService

import logging
logger = logging.getLogger('django.request')


def send_admin_user_signup_email(*args, **kwargs):
    user = kwargs.pop('user', None)

    if user is not None:
        logger.info('Sending User signed up admin notification email')
        SendEmailService.send_user_signedup_admin_email(user_list=[user])


def save_user_signup_preferences(*args, **kwargs):
    request = kwargs.get('request')
    user = kwargs.get('user')
    profile = user.userprofile

    profile.data['has_aggeed_t_and_c'] = request.POST.get('has_aggeed_t_and_c')
    profile.data['send_news_and_info'] = request.POST.get('send_news_and_info')
    profile.save(update_fields=['data'])
    # save


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        from .models import UserProfile
        profile, is_new = UserProfile.objects.get_or_create(user=instance)

