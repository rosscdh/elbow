# -*- coding: utf-8 -*-
from django import forms
from django.utils import formats
from django.conf import settings
from django.core import validators

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_countries.widgets import CountrySelectWidget

from pinax.eventlog.models import log

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Field, Submit, HTML, Button
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

YEARS = [year for year in xrange(1900, DATE_18_YEARS_AGO.year + 1)]


class CreateOrderForm(forms.Form):
    amount = forms.DecimalField(label=_('Amount to invest'),
                                max_digits=8,
                                decimal_places=0,
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
                              initial=_('Germany'),
                              required=True)

    payment_type = forms.ChoiceField(label=_('How to pay'),
                                     initial=ORDER_PAYMENT_TYPE.debit,
                                     choices=ORDER_PAYMENT_TYPE.get_choices(),
                                     help_text=_('Please select a payment type'),
                                     widget=forms.RadioSelect)

    disclosure = forms.BooleanField(label=_(u'You want to invest 1000,00 &euro; or more and therefore, must agree to the loan contract in order to proceed'),
                                    widget=forms.CheckboxInput,
                                    required=False)

    t_and_c = forms.BooleanField(label=_('I agree to the site <a target=\"_NEW\" href="{url}">Terms & Conditions</a>'),
                                 widget=forms.CheckboxInput)

    has_read_investment_contract = forms.BooleanField(label=_('I have read and agree to be bound to the terms of the <a target=\"_NEW\" href="{url}">investment contract</a>.'),
                                                      widget=forms.CheckboxInput)

    has_read_loan_agreement_contract = forms.BooleanField(label=_('I have read and agree to the terms of the <a target=\"_NEW\" href="{url}">loan agreement</a>.'),
                                                          widget=forms.CheckboxInput)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.project = kwargs.pop('project', None)

        self.available_from_message = None
        if self.project.date_available:
            available_from = formats.date_format(self.project.date_available, "SHORT_DATE_FORMAT")
            self.available_from_message = _(u'Available from %(available_from)s') % {'available_from': available_from}

        if self.user is None:
            raise Exception('user must be passed into the Form')
        if self.project is None:
            raise Exception('project must be passed into the Form')

        super(CreateOrderForm, self).__init__(**kwargs)
        self.fields['customer_first_name'].initial = self.user.first_name
        self.fields['customer_last_name'].initial = self.user.last_name

        #
        # Set minimum amount to that of the project
        # and the widget min value too
        #
        min_amount = int(self.project.minimum_investment.amount)
        self.fields['amount'].min_value = min_amount
        self.fields['amount'].widget.attrs['min'] = min_amount
        del self.fields['amount'].validators[0]
        self.fields['amount'].validators.append(validators.MinValueValidator(min_amount))

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
            self.fields['amount'].help_text = _(u'A minimum of {minimum} is required').format(minimum=unicode(self.project.minimum_investment))

        if self.project.maximum_investment:
            self.fields['amount'].help_text = _(u'A minimum of {minimum} and a maximum of {maximum}, is required').format(minimum=unicode(self.project.minimum_investment),
                                                                                                                          maximum=unicode(self.project.maximum_investment))
        # Setup the loan_agreement and term_sheet        
        self.fields['t_and_c'].label = self.fields['t_and_c'].label.format(url=settings.TERMS_AND_CONDITIONS_URL)

        if self.project.term_sheet_doc:
            self.fields['has_read_investment_contract'].label = self.fields['has_read_investment_contract'].label.format(url=self.project.term_sheet_doc.url)

        if self.project.loan_agreement_doc:
            self.fields['has_read_loan_agreement_contract'].label = self.fields['has_read_loan_agreement_contract'].label.format(url=self.project.loan_agreement_doc.url)

    @property
    def helper(self):
        helper = FormHelper(self)

        helper.form_action = ''
        helper.form_show_errors = True
        helper.render_unmentioned_fields = True

        show_has_agreed_to_loan_agreement_terms = 'hide'
        if self.is_large_sum() is True:
            show_has_agreed_to_loan_agreement_terms = ''

        if self.project.is_available_for_investment is True:
            form_submit_button = Submit('submit', _(u'Invest Now'), css_class='btn btn-primary btn-lg')
        else:
            form_submit_button = Button('button', self.available_from_message, css_class='btn btn-default btn-lg not-yet-available')

        helper.layout = Layout(
                               Fieldset(_('Investment Amount'),
                                        PrependedAppendedText('amount', DEFAULT_CURRENCY_SYMBOL, '.00'),
                                        HTML('<div class="input-group"><label for="" class="control-label">%s:</label>&nbsp;<span id="interest_rate_pa"></span></div>' % (_('Interest Rate p.a'),)),
                                        HTML('<div class="input-group"><label for="" class="control-label">%s:</label>&nbsp;<span id="interest_term"></span></div>' % (_('Interest Term'),)),
                                        HTML('<span id="accrue-target" class=""></span>'),
                                        HTML(u'<div id="loan-contract" class="{show_has_agreed_to_loan_agreement_terms} alert alert-warning clearfix">'.format(show_has_agreed_to_loan_agreement_terms=show_has_agreed_to_loan_agreement_terms)),
                                        Field('disclosure'),
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
                                        'has_read_investment_contract' if self.fields.get('has_read_investment_contract') else None,
                                        'has_read_loan_agreement_contract' if self.fields.get('has_read_loan_agreement_contract') else None,
                               ),
                               ButtonHolder(
                                    form_submit_button,
                               ))

        return helper

    def is_large_sum(self):
        if hasattr(self, 'cleaned_data') is True:
            return self.cleaned_data.get('amount', None) > 1000
        return False

    def clean(self, *args, **kwargs):
        # ensure we are able to do this
        if self.project.is_available_for_investment is False:
            raise forms.ValidationError(self.available_from_message,
                                        code='project_not_set_available',)
        return super(CreateOrderForm, self).clean(*args, **kwargs)

    def clean_disclosure(self, *args, **kwargs):
        if self.is_large_sum() is True and self.cleaned_data['disclosure'] is False:
                raise forms.ValidationError(_('You must confirm your self assessment of credit worthiness'),
                                            code='self_assessment_credit_worthiness',)
        return self.cleaned_data['disclosure']

    def clean_amount(self, *args, **kwargs):
        amount = self.data.get('amount', None)

        if amount and self.project.minimum_investment and \
           Decimal(amount) < self.project.minimum_investment.amount:
            raise forms.ValidationError(mark_safe(_(u'The minimum investment amount is {minimum}').format(minimum=unicode(self.project.minimum_investment.amount))),
                                        code='minimum_investment_amount_not_met',)
        if amount and self.project.maximum_investment and \
           Decimal(amount) > self.project.maximum_investment.amount:
            raise forms.ValidationError(mark_safe(_(u'The maximum investment amount is {maximum}').format(maximum=unicode(self.project.maximum_investment.amount))),
                                        code='maximum_investment_amount_not_met',)
        return self.cleaned_data['amount']

    def clean_has_read_loan_agreement_contract(self, *args, **kwargs):
        if self.cleaned_data.get('has_read_loan_agreement_contract'):
            if self.is_large_sum() is True and self.cleaned_data['has_read_loan_agreement_contract'] is False:
                    raise forms.ValidationError(_('You must agree to the terms of the loan agreement'),
                                                code='must_agree_to_terms_of_loan_agreement',)
        return self.cleaned_data['has_read_loan_agreement_contract']

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        disclosure = self.cleaned_data.pop('disclosure', None)
        t_and_c = self.cleaned_data.pop('t_and_c', None)
        has_read_investment_contract = self.cleaned_data.pop('has_read_investment_contract', None)
        has_read_loan_agreement_contract = self.cleaned_data.pop('has_read_loan_agreement_contract', None)

        amount = self.cleaned_data['amount']
        self.cleaned_data['amount'] = Money(Decimal(amount), EUR)

        self.cleaned_data['customer_name'] = '%s %s' % (self.cleaned_data.pop('customer_first_name', None),
                                                        self.cleaned_data.pop('customer_last_name', None))

        self.cleaned_data['user'] = self.user
        self.cleaned_data['project'] = self.project

        order = Order.objects.create(**self.cleaned_data)

        #
        # Make the payment
        #
        order, payment_api_response = order.make_payment(user=self.user)

        #
        # Create PDF and associate with Order
        #
        pdf_service = LoanAgreementCreatePDFService(order=order,
                                                    user=self.user)
        order = pdf_service.process()

        log(
            user=self.user,
            action="order.lifecycle.created",
            obj=order,
            extra={
                "note": "%s Created a new Order to Invest" % self.user,
                "is_large_amount": order.is_large_amount,
                "amount": unicode(order.amount),
                "disclosure": disclosure,
                "has_read_loan_agreement_contract": has_read_loan_agreement_contract,
                "t_and_c_agreed": t_and_c,
                "has_read_investment_contract": has_read_investment_contract,
                "email_with_loan_agreement_sent": False,
            }
        )

        return order


class OrderLoanAgreementForm(forms.Form):
    has_agreed_to_loan_agreement_terms = forms.BooleanField(label='',
                                                            help_text=_('I agree to the terms of the Loan Agreement'),
                                                            initial=True,
                                                            widget=forms.HiddenInput)

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
                               HTML('<br/>'),
                               ButtonHolder(
                                   Submit('submit', _('Continue & Make the payment'), css_class='btn btn-primary btn-lg'),))
        return helper

    def save(self, *args, **kwargs):
        """
        Artificial save here as forms.Form dont have a save method
        """
        has_agreed_to_loan_agreement_terms = self.cleaned_data.pop('has_agreed_to_loan_agreement_terms')

        #
        # Send email with PDF Attachment
        #
        email_service = SendEmailService(order=self.order)
        email_service.send_order_created_email(user_list=[self.user])

        self.order.status = self.order.ORDER_STATUS.loan_agreement
        self.order.data['has_agreed_to_loan_agreement_terms'] = has_agreed_to_loan_agreement_terms
        self.order.data['email_with_loan_agreement_sent'] = True
        self.order.save(update_fields=['status', 'data'])

        log(
            user=self.user,
            action="order.lifecycle.loan_agreement.accepted",
            obj=self.order,
            extra={
                "note": "%s Agreed to the large sum agreement" % self.user,
                "is_large_amount": self.order.is_large_amount,
                "amount": unicode(self.order.amount),
                "email_with_loan_agreement_sent": True,
            }
        )

        return self.order
