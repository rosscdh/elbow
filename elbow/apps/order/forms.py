# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from pinax.eventlog.models import log

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Field, Submit
from crispy_forms.bootstrap import PrependedAppendedText

from decimal import Decimal
from moneyed import Money, EUR

from elbow.apps.order.models import Order
from elbow.apps.order.services import LoanAgreementCreatePDFService

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
    address_1 = forms.CharField(label=_('Address'), help_text=_('Line 1 of address'), required=True)
    address_2 = forms.CharField(label='', help_text=_('Line 2 of address'), required=False)
    postcode = forms.CharField(label=_('Post code'), required=True)
    city = forms.CharField(label=_('City'), required=True)
    country = forms.CharField(label=_('Country'), required=True)

    tax_number = forms.CharField(label=_('Tax number'), required=True)

    payment_type = forms.ChoiceField(label=_('How to pay'),
                                     choices=ORDER_PAYMENT_TYPE.get_choices(),
                                     help_text=_('Please select a payment type'))

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
                                ),
                               Fieldset(_('Postal Address'),
                                        'address_1',
                                        'address_2',
                                        'postcode',
                                        'city',
                                        'country',
                               ),
                               Fieldset(_('Tax information'),
                                        'tax_number',
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

        address_1 = self.cleaned_data.pop('address_1')
        address_2 = self.cleaned_data.pop('address_2')
        postcode = self.cleaned_data.pop('postcode')
        city = self.cleaned_data.pop('city')

        amount = self.cleaned_data['amount']
        self.cleaned_data['amount'] = Money(Decimal(amount), EUR)

        self.cleaned_data['user'] = self.user
        self.cleaned_data['project'] = self.project

        order = Order.objects.create(**self.cleaned_data)

        #
        # Create PDF and associate with Order
        #
        pdf_service = LoanAgreementCreatePDFService(order=order,
                                                    user=self.user)
        order = pdf_service.process()

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


class OrderLoanAgreementForm(forms.Form):
    has_agreed_to_loan_agreement_terms = forms.BooleanField(label='',
                                                            help_text=_('I agree to the terms of the Loan Agreement'),
                                                            required=True)

    def __init__(self, *args, **kwargs):
        self.order = kwargs.pop('order', None)
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        self.document = self.order.documents.filter(user=self.user).first()  # most recent

        if self.order is None:
            raise Exception('order must be passed into the Form')
        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(OrderLoanAgreementForm, self).__init__(**kwargs)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True

        helper.layout = Layout(Fieldset('',
                                   Field('has_agreed_to_loan_agreement_terms'),
                               ),
                               ButtonHolder(
                                   Submit('submit', _('Submit'), css_class='btn btn-success btn-lg')
                               ))
        return helper

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        has_agreed_to_loan_agreement_terms = self.cleaned_data.pop('has_agreed_to_loan_agreement_terms')

        self.order.status = self.order.ORDER_STATUS.loan_agreement
        self.order.data['has_agreed_to_loan_agreement_terms'] = has_agreed_to_loan_agreement_terms
        self.order.save(update_fields=['status', 'data'])

        #
        # Send email with PDF Attachment
        #
        email_service = SendEmailService(order=self.order)
        email_service.send_order_loan_agreement_email(user_list=[self.user])

        log(
            user=self.user,
            action="order.lifecycle.loan_agreement.accepted",
            obj=self.order,
            extra={
                "note": "%s Agreed to the large sum agreement" % self.user
            }
        )

        return self.order
