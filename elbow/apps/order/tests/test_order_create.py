# -*- coding: UTF-8 -*-
from . import TestCase
from django.test import Client, SimpleTestCase
from django.core.urlresolvers import reverse

from elbow.apps.order.forms import CreateOrderForm
from elbow.apps.project.models import Project
from model_mommy import mommy

VALID_DATA = {
    'amount': 250,
    'customer_name': 'Bob Dylan Inc.',
    'phone': '555-55-55',
    'address': '46a BismarkStrasse Mönchengladbach, NRW',
    'country': 'Germany',
    'payment_type': 'bank_debit',
    't_and_c': True,
    'has_read_contract': True
}


class BaseTestCase(TestCase):
    def setUp(self):
        self.c = Client()


class OrderCreateViewTest(BaseTestCase):
    """
    Test basic model methods
    """
    fixtures = ['project.json']

    def setUp(self):
        super(OrderCreateViewTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.url = reverse('order:create', kwargs={'project_slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = VALID_DATA

    def test_form_redirects_to_login(self):
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/accounts/login/?next=/orders/my-basic-test-project/order/')

    def test_form_shows_to_authenticated(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['order/order-create.html'])
        self.assertEqual(resp.context['project'], self.project)
        self.assertEqual(type(resp.context['form']), CreateOrderForm)
        # Default sets the current usres name
        self.assertEqual(resp.context['form'].fields['customer_name'].initial, '%s %s' % (self.user.first_name, self.user.last_name))

    def test_form_redirects_to_payments_page_on_success(self):
        self.c.force_login(self.user)
        resp = self.c.post(self.url, self.initial)
        self.assertEqual(resp.status_code, 302)
        # shortUUIDHexMatch.search("/orders/my-basic-test-project/order/CQGsvHhfhfnsQQp4zRax2g/")
        # import pdb;pdb.set_trace()
        # self.assertEqual(resp.url, "/orders/my-basic-test-project/order/CQGsvHhfhfnsQQp4zRax2g/")


class OrderFormTest(TestCase):
    def setUp(self):
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.url = reverse('order:create', kwargs={'project_slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

        self.initial = VALID_DATA

    def test_invalid_form(self):
        # Test no data
        form = CreateOrderForm(user=self.user, project=self.project)
        self.assertTrue(form.is_valid() is False)

    def test_valid_form(self):
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

