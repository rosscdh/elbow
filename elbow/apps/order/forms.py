# -*- coding: utf-8 -*-
from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from pinax.eventlog.models import log

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Field, Submit, HTML
from crispy_forms.bootstrap import PrependedAppendedText

from decimal import Decimal
from moneyed import Money, EUR

from elbow.apps.order.models import Order
from elbow.apps.order.services import LoanAgreementCreatePDFService

from elbow.apps.public.services import SendEmailService
from .apps import ORDER_PAYMENT_TYPE

import datetime
from dateutil.relativedelta import relativedelta

DEFAULT_CURRENCY_SYMBOL = getattr(settings, 'DEFAULT_CURRENCY_SYMBOL', '€')
DATE_18_YEARS_AGO = datetime.datetime.today() - relativedelta(years=18)
DEFAULT_DATE = datetime.datetime.today() - relativedelta(years=25)

YEARS = [year for year in xrange(1930, DATE_18_YEARS_AGO.year -1)]


class CreateOrderForm(forms.Form):
    amount = forms.DecimalField(label=_('Investment Amount'),
                                max_digits=8,
                                decimal_places=2,
                                min_value=500,
                                required=True)

    title = forms.ChoiceField(label=_('Title'), choices=(('Mr', _('Mr')), ('Mrs', _('Mrs')),))

    customer_first_name = forms.CharField(label=_('First name'),
                                          required=True)

    customer_last_name = forms.CharField(label=_('Last name'),
                                         required=True)

    company_name = forms.CharField(label=_('Name of Company'),
                                   help_text=_('If applicable'),
                                   required=False)

    dob = forms.DateField(label=_('Date of Birth'),
                          initial=DEFAULT_DATE.date,
                          widget=forms.SelectDateWidget(years=YEARS))

    address_1 = forms.CharField(label=_('Address'),
                                help_text=_('Line 1 of address'),
                                required=True)

    address_2 = forms.CharField(label='',
                                help_text=_('Line 2 of address'),
                                required=False)

    postcode = forms.CharField(label=_('Post code'),
                               required=True)

    city = forms.CharField(label=_('City'),
                           required=True)

    country = forms.CharField(label=_('Country'),
                              required=True)

    payment_type = forms.ChoiceField(label=_('How to pay'),
                                     initial=ORDER_PAYMENT_TYPE.prepay,
                                     choices=ORDER_PAYMENT_TYPE.get_choices(),
                                     help_text=_('Please select a payment type'),
                                     widget=forms.RadioSelect)

    t_and_c = forms.BooleanField(label=_('I have read and agree to the Terms & Conditions'),
                                 widget=forms.CheckboxInput)

    has_read_investment_contract = forms.BooleanField(label=_('I have read and agree to be bound to the terms of the investment contract.'),
                                                      widget=forms.CheckboxInput)

    has_read_loan_agreement_contract = forms.BooleanField(label=_('I have read and agree to the terms of the loan agreement.'),
                                                          widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(CreateOrderForm, self).__init__(**kwargs)
        self.fields['customer_first_name'].initial = self.user.first_name
        self.fields['customer_last_name'].initial = self.user.last_name

        #
        # Setup minimum and max investment if the project has it
        # Order is important
        #
        if self.project.minimum_investment:
            self.fields['amount'].min_value = self.project.minimum_investment.amount

        if self.project.maximum_investment:
            self.fields['amount'].max_value = self.project.maximum_investment.amount

        #
        # Setup help text in the case of min and max investment
        # Order is important
        #
        if self.project.minimum_investment:
            self.fields['amount'].help_text = _(u'A minimum of &euro;{minimum} is required'.format(minimum=self.project.minimum_investment.amount))

        if self.project.maximum_investment:
            self.fields['amount'].help_text = _(u'A minimum of &euro;{minimum} and a maximum of &euro;{maximum}, is required'.format(minimum=self.project.minimum_investment.amount, maximum=self.project.maximum_investment.amount))

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        show_has_agreed_to_loan_agreement_terms = 'hide'
        if self.is_large_sum() is True:
            show_has_agreed_to_loan_agreement_terms = ''

        helper.layout = Layout(
                               Fieldset(_('Investment Amount'),
                                        PrependedAppendedText('amount', DEFAULT_CURRENCY_SYMBOL, '.00'),
                                        HTML('<div class="input-group"><label for="" class="control-label">%s:</label>&nbsp;<span id="interest_rate_pa"></span></div>' % (_('Interest Rate p.a'),)),
                                        HTML('<div class="input-group"><label for="" class="control-label">%s:</label>&nbsp;<span id="interest_term"></span></div>' % (_('Interest Term'),)),
                                        HTML('<span id="accrue-target" class=""></span>'),
                                        HTML(u'<div id="loan-contract" class="{show_has_agreed_to_loan_agreement_terms} alert alert-warning clearfix"><p>{text}</p>'.format(show_has_agreed_to_loan_agreement_terms=show_has_agreed_to_loan_agreement_terms, text=_(u'You want to invest 1000.00 or more and therefore, must agree to the loan contract in order to proceed'))),
                                        HTML('</div>'),
                               ),
                               Fieldset(_('Investor Details'),
                                        'title',
                                        'customer_first_name',
                                        'customer_last_name',
                                        'dob',
                               ),
                               Fieldset(_('Company Details'),
                                        'company_name',
                               ),
                               Fieldset(_('Postal Address'),
                                        'address_1',
                                        'address_2',
                                        'postcode',
                                        'city',
                                        'country',
                               ),
                               Fieldset(_('Payment'),
                                        'payment_type',
                                        't_and_c',
                                        'has_read_investment_contract',
                                        'has_read_loan_agreement_contract',
                               ),
                               ButtonHolder(
                                    Submit('submit', _('Invest Now'), css_class='btn btn-lg'),
                               ))
        return helper

    def is_large_sum(self):
        if hasattr(self, 'cleaned_data') is True:
            return self.cleaned_data.get('amount', None) >= 1000
        return False

    def clean_amount(self, *args, **kwargs):
        amount = self.data.get('amount', None)

        if amount and self.project.minimum_investment and \
           Decimal(amount) <= self.project.minimum_investment.amount:
            raise forms.ValidationError(mark_safe(_(u'The minimum investment amount is &euro;{minimum}'.format(minimum=self.project.minimum_investment.amount))),
                                        code='minimum_investment_amount_not_met',)
        if amount and self.project.maximum_investment and \
           Decimal(amount) > self.project.maximum_investment.amount:
            raise forms.ValidationError(mark_safe(_(u'The maximum investment amount is &euro;{maximum}'.format(maximum=self.project.maximum_investment.amount))),
                                        code='maximum_investment_amount_not_met',)
        return self.cleaned_data['amount']

    def clean_has_read_loan_agreement_contract(self, *args, **kwargs):
        if self.is_large_sum() is True and self.cleaned_data['has_read_loan_agreement_contract'] is False:
                raise forms.ValidationError(_('You must agree to the terms of the loan agreement'),
                                            code='must_agree_to_terms_of_loan_agreement',)
        return self.cleaned_data['has_read_loan_agreement_contract']

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        t_and_c = self.cleaned_data.pop('t_and_c')
        has_read_investment_contract = self.cleaned_data.pop('has_read_investment_contract')
        has_read_loan_agreement_contract = self.cleaned_data.pop('has_read_loan_agreement_contract')

        amount = self.cleaned_data['amount']
        self.cleaned_data['amount'] = Money(Decimal(amount), EUR)

        self.cleaned_data['customer_name'] = '%s %s' % (self.cleaned_data.pop('customer_first_name'),
                                                        self.cleaned_data.pop('customer_last_name'))

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
                "note": "%s Created a new Order to Invest" % self.user,
                "is_large_amount": order.is_large_amount,
                "amount": unicode(order.amount),
                "has_read_loan_agreement_contract": has_read_loan_agreement_contract,
                "t_and_c_agreed": t_and_c,
                "has_read_investment_contract": has_read_investment_contract,
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

        #
        # Hide the has_agreed_to_loan_agreement_terms field if the user
        # is not investing more than 1k
        #
        if self.order.is_large_amount is False:
            self.fields['has_agreed_to_loan_agreement_terms'].required = False
            self.fields['has_agreed_to_loan_agreement_terms'].widget = forms.HiddenInput()

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True

        helper.layout = Layout(Fieldset('',
                                        Field('has_agreed_to_loan_agreement_terms'),),
                               ButtonHolder(
                                   Submit('submit', _('Continue & Make the payment'), css_class='btn btn-primary btn-lg'),))
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
        if self.order.is_large_amount is True:
            email_service = SendEmailService(order=self.order)
            email_service.send_order_created_email(user_list=[self.user])

            log(
                user=self.user,
                action="order.lifecycle.loan_agreement.accepted",
                obj=self.order,
                extra={
                    "note": "%s Agreed to the large sum agreement" % self.user,
                    "is_large_amount": self.order.is_large_amount,
                    "amount": unicode(self.order.amount),
                }
            )

        return self.order
