# -*- coding: utf-8 -*-
from django import forms

from .models import Order


class BaseOrderForm(forms.ModelForm):
    amount = forms.IntegerField(label='Investment Amount')
    user = forms.CharField(widget=forms.HiddenInput)
    project = forms.CharField(widget=forms.HiddenInput)

    class Meta:
        model = Order
        exclude = ('updated_at', 'created_at',)

    def __init__(self, user, project, *args, **kwargs):
        super(BaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['user'].initial = user
        self.fields['project'].initial = project


class CreateOrderForm(BaseOrderForm):
    customer_name = forms.CharField(label='Name of Investor Person/Company')
    t_and_c = forms.BooleanField(label='', help_text='I agree to the terms and conditions', widget=forms.CheckboxInput)
    read_contract = forms.BooleanField(label='', help_text='I have read and agree to be bound to the terms of the contract document', widget=forms.CheckboxInput)

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
