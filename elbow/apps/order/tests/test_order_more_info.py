# -*- coding: UTF-8 -*-
from . import BaseTestCase, TestCase
from django.core import mail
from django.core.urlresolvers import reverse

from elbow.apps.order.forms import OrderMoreInfoForm

from model_mommy import mommy

import re


class OrderMoreInfoViewTest(BaseTestCase):
    def setUp(self):
        super(OrderMoreInfoViewTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.order = mommy.make('order.Order', project=self.project, amount=250.00)
        self.url = reverse('order:more_info', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = {
            'has_provided_additional_data': True
        }

    def test_form_redirects_to_large_sum_agreements_page_on_success(self):
        self.order.amount = 5500.00
        self.order.save(update_fields=['amount'])
        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/large-sum-agreement/' % self.order.uuid)

    def test_form_redirects_to_payments_page_due_to_small_amount(self):
        self.order.amount = 250.00
        self.order.save(update_fields=['amount'])
        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/payment/' % self.order.uuid)


class OrderMoreInfoFormTest(TestCase):
    def setUp(self):
        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.order = mommy.make('order.Order', project=self.project, amount=250.00, user=self.user)

        self.initial = {
            'has_provided_additional_data': True
        }
        mail.outbox = []

    def test_invalid_form(self):
        # Test no data
        form = OrderMoreInfoForm(user=self.user, project=self.project, order=self.order)
        self.assertTrue(form.is_valid() is False)

    def test_valid_form(self):
        with self.settings(DEBUG=True):

            # Test with data
            form = OrderMoreInfoForm(user=self.user,
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
        attachment_filename_pattern = re.compile('order-documentorder-info-agreement_(.+?).pdf')

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
