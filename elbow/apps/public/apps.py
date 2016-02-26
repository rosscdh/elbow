# -*- coding: UTF-8 -*-
from django.apps import AppConfig

from allauth.account.signals import user_signed_up
from .handlers import send_admin_user_signup_email


class PublicConfig(AppConfig):
    name = 'elbow.apps.public'

    def ready(self):
        user_signed_up.connect(send_admin_user_signup_email,
            dispatch_uid="public.user.signup")
