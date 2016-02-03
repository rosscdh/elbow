# -*- coding: UTF-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse

from elbow.utils import get_namedtuple_choices
from elbow.apps.project.models import Project

from model_mommy import mommy

from . import BaseTestCase


SECUPAY_STATES = get_namedtuple_choices('SECUPAY_STATES', (
    ('accepted', 'accepted', 'Accepted'),
    ('authorized', 'authorized', 'Authorized'),
    ('denied', 'denied', 'Denied'),
    ('issue', 'issue', 'Issue'),
    ('void', 'void', 'Void'),
    ('issue_resolved', 'issue_resolved', 'Issue Resolved'),
))

POST_DATA = {
    'hash': 'jtnjpfgrbrqk3300',
    'amount': 25.00,
    'status_id': '',
    'status_description': 'Test Case',
    'changed': '',
    'apikey': '',
    'hint': '',
    'payment_status': '',
    'simplifiedstatus': SECUPAY_STATES.authorized,
}


class OrderWebhookTest(BaseTestCase):
    def setUp(self):
        super(OrderWebhookTest, self).setUp()
        self.project = Project.objects.all().first()
        self.order = mommy.make('order.Order',
                                project=self.project,
                                transaction_id=POST_DATA.get('hash'),
                                amount=POST_DATA.get('amount'))

        self.url = reverse('order:payment_webhook', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

        self.initial = POST_DATA
        mail.outbox = []

    def test_url(self):
        self.assertEqual(self.url, u'/de/orders/%s/order/%s/payment/webhook/' % (self.project.slug, self.order.uuid))

    def test_valid_post(self):
        # Test with data
        self.assertEqual(len(self.order.log_history), 0)
        resp = self.c.post(self.url, self.initial)

        self.assertEqual(resp.status_code, 200)
        self.assertTrue('ack=Approved' in resp.content)

        # Recorded in order history?
        history = self.order.log_history
        self.assertEqual(len(history), 1)

    def test_404_post(self):
        # Test with data
        post_data = self.initial.copy()
        post_data['hash'] = '123WRONG'
        self.assertEqual(len(self.order.log_history), 0)
        resp = self.c.post(self.url, post_data)

        self.assertEqual(resp.status_code, 400)
        self.assertTrue('ack=Disapproved' in resp.content)

        expected_error_message = 'error=Order+with+transaction_id+of+123WRONG+does+not+exist'
        self.assertTrue(expected_error_message in resp.content)

        # Recorded in order history?
        history = self.order.log_history
        self.assertEqual(len(history), 0)

