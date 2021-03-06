# -*- coding: UTF-8 -*-
from . import BaseTestCase, TestCase, VALID_ORDER_POST_DATA
from django.core import mail
from django.core.urlresolvers import reverse

import json
import datetime
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
        
        self.project.documents.add(mommy.make('document.Document', name=u'Exposé'))
        self.project.documents.add(mommy.make('document.Document', name=u'Finanzplan'))

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
        self.assertEqual(resp.context['form'].fields['customer_first_name'].initial, self.user.first_name)
        self.assertEqual(resp.context['form'].fields['customer_last_name'].initial, self.user.last_name)

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

        expected_response = {u'status': u'ok', u'errors': None, u'data': {u'status': u'proceed', u'hash': u'xfquhyrguiub967897', u'created': u'2016-08-23 14:42:10', u'demo': 1, u'amount': 150000, u'trans_id': u'6088759'}}
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/status",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        # This is to ensure we redirect to the loan_agreement page
        self.assertEqual(self.initial.get('amount'), 2500)

        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            # initial amount is 2500
            resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 302)

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

        expected_response = {u'status': u'ok', u'errors': None, u'data': {u'status': u'proceed', u'hash': u'xfquhyrguiub967897', u'created': u'2016-08-23 14:42:10', u'demo': 1, u'amount': 150000, u'trans_id': u'6088759'}}
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/status",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        # This is to ensure we redirect to the loan_agreement page
        self.initial['amount'] = 501
        self.assertEqual(self.initial.get('amount'), 501)

        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            # initial amount is 2500
            resp = self.c.post(self.url, self.initial)

        self.assertTrue(len(self.project.order_set.all()) == 1)
        order = self.project.order_set.all().first()

        #
        # Redirected to more loan-agreement page as well so they have opportunity to DL agreement
        #
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/orders/my-basic-test-project/order/%s/loan-agreement/' % order.uuid)

    @httpretty.activate
    def test_form_raises_permission_denied_if_date_available_not_valid(self):
        tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
        self.project.date_available = tomorrow
        self.project.save(update_fields=['date_available'])

        with self.settings(DEBUG=True):
            self.c.force_login(self.user)
            # initial amount is 2500
            resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 200)

        self.assertTrue('<div class="alert alert-block alert-danger"><ul><li>m\xc3\xb6glich ab' in resp.content)


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
    def test_valid_debit_form(self):
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

        expected_response = {u'status': u'ok', u'errors': None, u'data': {u'status': u'proceed', u'hash': u'xfquhyrguiub967897', u'created': u'2016-08-23 14:42:10', u'demo': 1, u'amount': 150000, u'trans_id': u'6088759'}}
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/status",
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

        # Should be no documents attached YET
        self.assertEqual(order.documents.all().count(), 1)

        # NO Emails should be sent right after the make_payment has been called
        self.assertEqual(0, len(mail.outbox))

    @httpretty.activate
    def test_valid_prepay_form(self):
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

        expected_response = {u'status': u'ok', u'errors': None, u'data': {u'status': u'proceed', u'hash': u'xfquhyrguiub967897', u'created': u'2016-08-23 14:42:10', u'demo': 1, u'amount': 150000, u'trans_id': u'6088759'}}
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/status",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        with self.settings(DEBUG=True):

            # Test with data
            prepay_data = self.initial.copy()
            prepay_data.update({'payment_type': 'prepay'})
            form = CreateOrderForm(user=self.user, project=self.project, data=prepay_data)
            self.assertTrue(form.is_valid())
            order = form.save()

        self.assertEqual(order.__class__.__name__, 'Order')

        assert order.uuid
        assert order.pk

        self.assertEqual(order.amount.__class__.__name__, 'MoneyPatched')

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.project, self.project)

        # No documents yet
        self.assertEqual(order.documents.all().count(), 1)

        # Should have email to managers AND email to customer
        self.assertEqual(0, len(mail.outbox))
