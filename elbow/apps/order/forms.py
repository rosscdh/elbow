# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import PrependedAppendedText

from elbow.apps.project.models import Project

from .models import Order

DEFAULT_CURRENCY_SYMBOL = getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '€')


class BaseOrderForm(forms.ModelForm):
    amount = forms.IntegerField(label=_('Investment Amount'))

    amount_currency = forms.CharField(initial=DEFAULT_CURRENCY_SYMBOL,
                                      widget=forms.HiddenInput)

    user = forms.ModelChoiceField(queryset=get_user_model().objects.all(),
                                  widget=forms.HiddenInput)

    project = forms.ModelChoiceField(queryset=Project.objects.all(),
                                     widget=forms.HiddenInput)

    class Meta:
        model = Order
        exclude = ('updated_at', 'created_at',)

    def __init__(self, user, project, *args, **kwargs):
        super(BaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['user'].initial = user
        self.fields['project'].initial = project


class CreateOrderForm(BaseOrderForm):
    customer_name = forms.CharField(label=_('Name of Investor Person/Company'))

    t_and_c = forms.BooleanField(label=None,
                                 help_text=_('I agree to the terms and conditions'),
                                 widget=forms.CheckboxInput)

    read_contract = forms.BooleanField(label=None,
                                       help_text=_('I have read and agree to be bound to the terms of the contract document'),
                                       widget=forms.CheckboxInput)

    class Meta(BaseOrderForm.Meta):
        fields = ('amount',
                  'customer_name',
                  'phone',
                  'address',
                  'country',
                  'user',
                  'project',)

    def __init__(self, user, project, *args, **kwargs):
        super(CreateOrderForm, self).__init__(user, project, *args, **kwargs)
        self.fields['customer_name'].initial = user.first_name
        self.fields['user'].initial = user
        self.fields['project'].initial = project

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        helper.layout = Layout(
          Fieldset(
                'Investment Amount',
                PrependedAppendedText('amount', DEFAULT_CURRENCY_SYMBOL, '.00'),
                'user',
                'project',
            ),
          Fieldset(
                'Investor Details',
                'customer_name',
                'phone',
                'address',
                'country',
                't_and_c',
                'read_contract',
            ),
            ButtonHolder(
                Submit('submit', _('Submit'), css_class='button white')
            )
        )
        return helper
