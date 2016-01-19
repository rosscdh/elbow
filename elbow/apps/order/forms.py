# -*- coding: utf-8 -*-
from django import forms

from .models import Order


class BaseOrderForm(forms.ModelForm):
    user = None
    project = None

    class Meta:
        model = Order
        exclude = ('updated_at', 'created_at',)

    def __init__(self, user, project, *args, **kwargs):
        super(BaseOrderForm, self).__init__(*args, **kwargs)
        self.fields['user'].initial = user
        self.fields['project'].initial = project


class CreateOrderForm(BaseOrderForm):
    class Meta(BaseOrderForm.Meta):
        fields = ('amount', 'user', 'project',)
