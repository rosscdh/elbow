# -*- coding: UTF-8 -*-
from . import BaseTestCase, TestCase, VALID_ORDER_POST_DATA
from django.core.urlresolvers import reverse
from django.core import mail

import json
import httpretty

from elbow.apps.order.forms import CreateOrderForm
from model_mommy import mommy


class OrderCreateViewTest(BaseTestCase):
    """
    Test basic view flow
    """
    def setUp(self):
        super(OrderCreateViewTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.url = reverse('order:create', kwargs={'project_slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = VALID_ORDER_POST_DATA

    def test_form_redirects_to_login(self):
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/accounts/login/?next=/de/orders/my-basic-test-project/order/')

    def test_form_shows_to_authenticated(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['order/order-create.html'])
        self.assertEqual(resp.context['project'], self.project)
        self.assertEqual(type(resp.context['form']), CreateOrderForm)
        # Default sets the current usres name
        self.assertEqual(resp.context['form'].fields['customer_name'].initial, '%s %s' % (self.user.first_name, self.user.last_name))

    @httpretty.activate
    def test_form_redirects_to_load_agreement_with_large_amount_page_on_success(self):
        expected_response = {
            "status": "ok",
            "data": {
                "hash": "tujevzgobryk3303",
                "iframe_url": "https://api.secupay.ag/payment/tujevzgobryk3303"
            },
            "errors": None
        }
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/init",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        # This is to ensure we redirect to the loan_agreement page
        self.assertEqual(self.initial.get('amount'), 2500)

        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            # initial amount is 2500
            resp = self.c.post(self.url, self.initial)

        self.assertTrue(len(self.project.order_set.all()) == 1)
        order = self.project.order_set.all().first()

        #
        # Redirected to more info page
        #
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/loan-agreement/' % order.uuid)

    @httpretty.activate
    def test_form_redirects_to_payment_with_small_amount_page_on_success(self):
        expected_response = {
            "status": "ok",
            "data": {
                "hash": "tujevzgobryk3303",
                "iframe_url": "https://api.secupay.ag/payment/tujevzgobryk3303"
            },
            "errors": None
        }
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/init",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        # This is to ensure we redirect to the loan_agreement page
        self.initial['amount'] = 500
        self.assertEqual(self.initial.get('amount'), 500)

        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            # initial amount is 2500
            resp = self.c.post(self.url, self.initial)

        self.assertTrue(len(self.project.order_set.all()) == 1)
        order = self.project.order_set.all().first()

        #
        # Redirected to more info page
        #
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/payment/' % order.uuid)


class OrderFormTest(TestCase):
    def setUp(self):
        self.project = mommy.make('project.Project', name='My Basic Test Project')

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = VALID_ORDER_POST_DATA
        mail.outbox = []

    def test_invalid_form(self):
        # Test no data
        form = CreateOrderForm(user=self.user, project=self.project)
        self.assertTrue(form.is_valid() is False)

    @httpretty.activate
    def test_valid_form(self):
        expected_response = {
            "status": "ok",
            "data": {
                "hash": "tujevzgobryk3303",
                "iframe_url": "https://api.secupay.ag/payment/tujevzgobryk3303"
            },
            "errors": None
        }
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/init",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        with self.settings(DEBUG=True):

            # Test with data
            form = CreateOrderForm(user=self.user, project=self.project, data=self.initial)

            self.assertTrue(form.is_valid())
            order = form.save()

        self.assertEqual(order.__class__.__name__, 'Order')

        assert order.uuid
        assert order.pk

        self.assertEqual(order.amount.__class__.__name__, 'MoneyPatched')

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.project, self.project)

        # Should create a document for the user if a large sum
        self.assertEqual(order.documents.all().count(), 1)

        # Should have email to managers AND email to customer
        self.assertEqual(2, len(mail.outbox))
        email = mail.outbox[0]
        self.assertEqual(unicode(email.subject), u'TodayCapital.de - a new order has been created')
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])

        email = mail.outbox[1]
        self.assertEqual(unicode(email.subject), u'TodayCapital.de - Your Investment Order has been created')
        self.assertEqual(email.recipients(), [self.user.email])
