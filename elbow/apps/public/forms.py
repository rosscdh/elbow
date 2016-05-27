# -*- coding: UTF-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Field, Submit

from allauth.account.forms import SignupForm as AllAuthSignupForm


class SignUpForm(AllAuthSignupForm):
    first_name = forms.CharField(label=_('First name'), required=True)
    last_name = forms.CharField(label=_('Last name'), required=True)

    has_aggeed_t_and_c = forms.BooleanField(label='',
                                            help_text=_('I agree to the site <a href="{url}">Terms & Conditions</a>').format(url=settings.TERMS_AND_CONDITIONS_URL),
                                            required=True,
                                            widget=forms.CheckboxInput)
    send_news_and_info = forms.NullBooleanField(label='',
                                                help_text=_('I would like to receive occasional news and information'),
                                                widget=forms.CheckboxInput)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        helper.layout = Layout(Fieldset(_('Personal Details'),
                                        Field('first_name', css_class='col-sm-6'),
                                        Field('last_name', css_class='col-sm-6'),),
                               Fieldset(_('Login Information'),
                                        Field('email'),
                                        Field('password1'),
                                        Field('password2'),),
                               Fieldset(_('Agreement & Newsletter'),
                                        Field('has_aggeed_t_and_c'),
                                        Field('send_news_and_info'),),
                               ButtonHolder(Submit('submit', _('Register Now'), css_class='btn btn-primary btn-lg'),))
        return helper
