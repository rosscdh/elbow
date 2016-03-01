# -*- coding: UTF-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
from allauth.account.forms import SignupForm as AllAuthSignupForm


class SignUpForm(AllAuthSignupForm):
    has_aggeed_t_and_c = forms.BooleanField(label='',
                                            help_text=_('I have read & agree to the Terms & Conditions and Data Protection agreement'),
                                            required=True,
                                            widget=forms.CheckboxInput)
    send_news_and_info = forms.NullBooleanField(label='',
                                                help_text=_('I would like to receive occasional news and information'),
                                                widget=forms.CheckboxInput)

