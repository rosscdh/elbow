# -*- coding: UTF-8 -*-
from django.core import mail
from django.test import SimpleTestCase

from model_mommy import mommy
from elbow.apps.order.models import Order


class BaseTestCase(SimpleTestCase):
    fixtures = ['project.json']


class SendForPaymentServiceTest(BaseTestCase):
    """
    UnitTest the service methods, with a VALID order object
    """

    def setUp(self):
        super(SendForPaymentServiceTest, self).setUp()
        mail.outbox = []
        self.order = mommy.prepare('order.Order',
                                   status=Order.ORDER_STATUS.processing,  # Must be in processing
                                   transaction_id=None)  # AND must NOT have a transaction_id
        self.order.user.email = 'bob@example.com'  # Set the email of the order User

    def test_should_send_for_payment(self):
        self.assertTrue(self.order.can_send_payment is True)


class SendForPaymentServiceInvalidTest(BaseTestCase):
    def test_invalid_status_payment_not_sent(self):
        for status in [Order.ORDER_STATUS.pending,
                       Order.ORDER_STATUS.new,
                       Order.ORDER_STATUS.paid,
                       Order.ORDER_STATUS.canceled]:
            order = mommy.prepare('order.Order', status=status)
            self.assertTrue(order.can_send_payment is False)

    def test_payment_has_transaction_id_and_not_sent(self):
        """
        DONT send the email, even if status is "processing"
        and we have a transaction_id
        """
        order = mommy.prepare('order.Order',
                              status=Order.ORDER_STATUS.processing,
                              transaction_id='abc123ABC')

        self.assertTrue(order.can_send_payment is False)
