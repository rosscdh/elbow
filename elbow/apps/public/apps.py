# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from allauth.account.signals import user_signed_up
from .handlers import send_admin_user_signup_email
from .handlers import save_user_signup_preferences
from .handlers import create_user_profile


class PublicConfig(AppConfig):
    name = 'elbow.apps.public'

    def ready(self):
        user_signed_up.connect(send_admin_user_signup_email,
                               dispatch_uid="public.user.signup")

        user_signed_up.connect(save_user_signup_preferences,
                               dispatch_uid="public.user.signup.preferences")

        post_save.connect(create_user_profile,
                          sender=get_user_model(),
                          dispatch_uid="public.user.signup.create_user_profile")

