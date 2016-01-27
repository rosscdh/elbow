# -*- coding: UTF-8 -*-
from . import BaseTestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy


class OrderAdminViewCallsTest(BaseTestCase):
    """
    Test basic admin view custom methods
    """
    def setUp(self):
        super(OrderAdminViewCallsTest, self).setUp()
        self.project = mommy.make('project.Project', name='My Basic Test Project')

        user_dict = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'is_staff': True,  # Must be staff
        }
        self.user = mommy.make('auth.User', **user_dict)

    def test_send_for_payment(self):
        order = mommy.make('order.Order', project=self.project, status='new')

        self.c.force_login(self.user)
        url = reverse('admin:order_send_for_payment', kwargs={'uuid': order.uuid})

        self.assertEqual(url, u'/admin/order/order/%s/send/' % order.uuid)
        self.assertTrue(order.status is 'new')

        resp = self.c.post(url, {})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {})

        # refresh
        order.refresh_from_db()

        self.assertTrue(order.status == 'processing')

    def test_cancel_order(self):
        order = mommy.make('order.Order', project=self.project, status='new')

        self.c.force_login(self.user)
        url = reverse('admin:order_cancel', kwargs={'uuid': order.uuid})

        self.assertEqual(url, u'/admin/order/order/%s/cancel/' % order.uuid)
        self.assertTrue(order.status is 'new')

        resp = self.c.post(url, {})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {})

        # refresh
        order.refresh_from_db()

        self.assertTrue(order.status == 'cancelled')

    def test_log_event(self):
        order = mommy.make('order.Order', project=self.project, status='new')

        self.assertEqual(len(order.log_history), 0)

        self.c.force_login(self.user)
        url = reverse('admin:order_add_log', kwargs={'uuid': order.uuid})

        self.assertEqual(url, u'/admin/order/order/%s/log/' % order.uuid)

        resp = self.c.post(url, {'note': 'My Test Note'})

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {})

        # refresh
        order.refresh_from_db()

        history = order.log_history
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].extra.get('note'), 'My Test Note')
