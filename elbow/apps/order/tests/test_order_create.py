# -*- coding: UTF-8 -*-
from . import TestCase
from django.test import Client
from django.core.urlresolvers import reverse

from elbow.apps.order.forms import CreateOrderForm
from model_mommy import mommy


class BaseTestCase(TestCase):
    def setUp(self):
        self.c = Client()


class OrderCreateTest(BaseTestCase):
    """
    Test basic model methods
    """
    def setUp(self):
        super(OrderCreateTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')
        self.url = reverse('order:create', kwargs={'project_slug': self.project.slug})

    def test_form_redirects_to_login(self):
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/accounts/login/?next=/orders/my-basic-test-project/order/')

    def test_form_shows_to_authenticated(self):
        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        user = mommy.make('auth.User', **user_dict)

        self.c.force_login(user)
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.template_name, ['order/order-create.html'])
        self.assertEqual(resp.context['project'], self.project)
        self.assertEqual(type(resp.context['form']), CreateOrderForm)

