# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from pinax.eventlog.models import log

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from crispy_forms.bootstrap import PrependedAppendedText

from decimal import Decimal
from moneyed import Money, EUR

from elbow.apps.order.models import Order
from elbow.apps.order.services import CreateMoreInfoAgreementPDFService

from elbow.apps.public.services import SendEmailService
from .apps import ORDER_PAYMENT_TYPE


DEFAULT_CURRENCY_SYMBOL = getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '€')


class CreateOrderForm(forms.Form):
    amount = forms.DecimalField(label=_('Investment Amount'),
                                max_digits=8,
                                decimal_places=2,
                                min_value=250,
                                required=True)

    customer_name = forms.CharField(label=_('Name of Investor Person/Company'),
                                    required=True)

    phone = forms.CharField(label=_('Telephone'), required=True)
    address = forms.CharField(label=_('Address'), widget=forms.Textarea, required=True)
    country = forms.CharField(label=_('Country'), required=True)

    payment_type = forms.ChoiceField(label=_('How to Pay'),
                                     choices=ORDER_PAYMENT_TYPE.get_choices(),
                                     help_text=_(''))

    t_and_c = forms.BooleanField(label=_('Terms & Conditions'),
                                 help_text=_('I agree to the terms and conditions'),
                                 widget=forms.CheckboxInput)

    has_read_contract = forms.BooleanField(label=_('I have read the contract'),
                                           help_text=_('I agree to be bound to the terms of the contract.'),
                                           widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(CreateOrderForm, self).__init__(**kwargs)
        self.fields['customer_name'].initial = '%s %s' % (self.user.first_name, self.user.last_name)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        helper.layout = Layout(
                               Fieldset(_('Investment Amount'),
                                        PrependedAppendedText('amount', DEFAULT_CURRENCY_SYMBOL, '.00'),
                               ),
                               Fieldset(_('Investor Details'),
                                        'customer_name',
                                        'phone',
                                        'address',
                                        'country',
                               ),
                               Fieldset(_('Payment, Terms & Download Contract'),
                                        'payment_type',
                                        't_and_c',
                                        'has_read_contract',
                               ),
                               ButtonHolder(
                                            Submit('submit', _('Submit'), css_class='btn btn-success btn-lg')
                               ))
        return helper

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        t_and_c = self.cleaned_data.pop('t_and_c')
        has_read_contract = self.cleaned_data.pop('has_read_contract')

        amount = self.cleaned_data['amount']
        self.cleaned_data['amount'] = Money(Decimal(amount), EUR)

        self.cleaned_data['user'] = self.user
        self.cleaned_data['project'] = self.project

        order = Order.objects.create(**self.cleaned_data)

        email_service = SendEmailService(order=order)
        email_service.send_order_created_email(user_list=[self.user])

        log(
            user=self.user,
            action="order.lifecycle.created",
            obj=order,
            extra={
                "note": "%s Created a new Order to Invest" % self.user
            }
        )

        return order


class OrderMoreInfoForm(forms.Form):
    junk = forms.CharField(label=_('Name of Investor Person/Company'),
                           required=True)

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        if self.order is None:
            raise Exception('order must be passed into the Form')
        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(OrderMoreInfoForm, self).__init__(**kwargs)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        helper.layout = Layout(
                               Fieldset(_('Additional Investor Info'),
                                        'junk',
                               ),
                               ButtonHolder(
                                    Submit('submit', _('Submit'), css_class='btn btn-success btn-lg')
                               ))
        return helper

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        self.cleaned_data['user'] = self.user
        self.cleaned_data['project'] = self.project

        #
        # Create PDF and associate with Order
        #
        pdf_service = CreateMoreInfoAgreementPDFService(order=self.order,
                                                        user=self.user)
        self.order = pdf_service.process()

        #
        # Send email with PDF Attachment
        #
        email_service = SendEmailService(order=self.order)
        email_service.send_order_more_info_email(user_list=[self.user])

        log(
            user=self.user,
            action="order.lifecycle.customer_provided_more_info",
            obj=self.order,
            extra={
                "note": "%s Created a new Order to Invest" % self.user
            }
        )

        return self.order


class OrderLargeSumAgreementForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        if self.order is None:
            raise Exception('order must be passed into the Form')
        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(OrderMoreInfoForm, self).__init__(**kwargs)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        helper.layout = Layout(
                               Fieldset(_('Additional Investor Info'),
                                        'customer_name',
                                        'phone',
                                        'address',
                                        'country',
                               ),
                               ButtonHolder(
                                    Submit('submit', _('Submit'), css_class='btn btn-success btn-lg')
                               ))
        return helper

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        t_and_c = self.cleaned_data.pop('t_and_c')
        has_read_contract = self.cleaned_data.pop('has_read_contract')

        amount = self.cleaned_data['amount']
        self.cleaned_data['amount'] = Money(Decimal(amount), EUR)

        self.cleaned_data['user'] = self.user
        self.cleaned_data['project'] = self.project

        email_service = SendEmailService(order=self.order)
        email_service.send_order_created_email(user_list=[self.user])

        log(
            user=self.user,
            action="order.lifecycle.large_sum_agreement.accepted",
            obj=self.order,
            extra={
                "note": "%s Agreed to the large sum agreement" % self.user
            }
        )

        return self.order
