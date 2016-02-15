# -*- coding: UTF-8 -*-
from . import BaseTestCase, TestCase
from django.core import mail
from django.core.urlresolvers import reverse

from elbow.apps.order.forms import OrderLoanAgreementForm
from elbow.apps.order.services import LoanAgreementCreatePDFService

from model_mommy import mommy

import re


class OrderLoanAgreementViewTest(BaseTestCase):
    def setUp(self):
        super(OrderLoanAgreementViewTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.order = mommy.make('order.Order', project=self.project, amount=250.00)
        self.url = reverse('order:loan_agreement', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = {
            'has_agreed_to_loan_agreement_terms': True
        }

    def test_form_shows_correct_html(self):
        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('<p>Ich bestätige, dass ich entweder über ein frei verfügbares Vermögen in Form von Bankguthaben und Finanzinstrumenten von mindestens 100.000 € verfüge</p><p>ODER dass der Gesamtbetrag meiner Investition in dieses Projekt nicht das Zweifache meines durchschnittlichen mtl. Nettoeinkommens übersteigt.</p>' in resp.content)

    def test_form_redirects_to_payment_page_on_success(self):
        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/payment/' % self.order.uuid)


class OrderLoanAgreementFormTest(TestCase):
    def setUp(self):
        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.order = mommy.make('order.Order',
                                project=self.project,
                                amount=250.00,
                                user=self.user)

        self.initial = {
            'has_agreed_to_loan_agreement_terms': True
        }
        mail.outbox = []

    def test_invalid_form(self):
        # Test no data
        form = OrderLoanAgreementForm(user=self.user, project=self.project, order=self.order)
        self.assertTrue(form.is_valid() is False)

    def test_valid_form(self):
        with self.settings(DEBUG=True):

            #
            # Create PDF and associate with Order, has to be done manually here
            # as this event happens in the Create order step and not the form
            # confirm validation step
            #
            pdf_service = LoanAgreementCreatePDFService(order=self.order,
                                                        user=self.order.user)
            pdf_service.process()

            # Test with data
            form = OrderLoanAgreementForm(user=self.user,
                                          project=self.project,
                                          order=self.order,
                                          data=self.initial)

            self.assertTrue(form.is_valid())
            order = form.save()

        self.assertEqual(order.__class__.__name__, 'Order')

        assert order.uuid
        assert order.pk

        self.assertEqual(order.amount.__class__.__name__, 'MoneyPatched')

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.project, self.project)

        # django adds a unique string to the attachement
        attachment_filename_pattern = re.compile('order-documentorder-loan-agreement_(.+?).pdf')

        # Should have email to managers AND email to customer
        self.assertEqual(2, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(unicode(email.subject), u'TodayCapital.de - Investment order provided more information')
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])

        self.assertEqual(len(email.attachments), 1)
        self.assertTrue(attachment_filename_pattern.match(email.attachments[0][0]))
        self.assertEqual(email.attachments[0][2], 'application/pdf')

        email = mail.outbox[1]
        self.assertEqual(unicode(email.subject), u'TodayCapital.de - Your Investment Order Info, Attached Agreement')
        self.assertEqual(email.recipients(), [self.user.email])

        self.assertEqual(len(email.attachments), 1)
        self.assertTrue(attachment_filename_pattern.match(email.attachments[0][0]))
        self.assertEqual(email.attachments[0][2], 'application/pdf')
