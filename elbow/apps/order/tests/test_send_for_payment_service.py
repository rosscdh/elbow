# -*- coding: UTF-8 -*-
from . import BaseTestCase
from django.core import mail
from django.test import SimpleTestCase

from model_mommy import mommy
from elbow.apps.order.models import Order
from elbow.apps.order.services import SendForPaymentService


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

        self.subject = SendForPaymentService(order=self.order)

    def test_should_send_for_payment(self):
        self.assertTrue(self.subject.should_send_for_payment() is True)

    def test_send_payment(self):
        self.assertEqual(self.subject.send_payment(), {})

    def test_send_success_email(self):
        result = self.subject.send_success_email(user_list=[self.order.user])  # Send the email
        # Should have email to managers AND email to customer
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(type(result), list)
        self.assertEqual(result, [('founders', 1), ('customer', 1)])

        for email in mail.outbox:
            self.assertEqual(email.subject, 'TodayCapital.de - Investment Payment, Success')

        email = mail.outbox[0]  # 0 should be to the Founders
        self.assertEqual(email.recipients(), ['founders@todaycapital.de'])

        email = mail.outbox[1]  # 1 should be to the Customers
        self.assertEqual(email.recipients(), [self.order.user.email])

    def test_send_fail_email(self):
        result = self.subject.send_fail_email()  # Send the email
        # Should have email to managers ONLY
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(type(result), list)
        self.assertEqual(result, [('founders', 1)])
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'TodayCapital.de - Investment Payment, Failure')
        self.assertEqual(email.recipients(), ['founders@todaycapital.de'])


class SendForPaymentServiceInvalidTest(BaseTestCase):
    def test_invalid_status_payment_not_sent(self):
        for status in [Order.ORDER_STATUS.pending,
                       Order.ORDER_STATUS.paid,
                       Order.ORDER_STATUS.failed,
                       Order.ORDER_STATUS.cancelled]:
            order = mommy.prepare('order.Order', status=status)
            subject = SendForPaymentService(order=order)
            self.assertTrue(subject.should_send_for_payment() is False)

    def test_payment_has_transaction_id_and_not_sent(self):
        """
        DONT send the email, even if status is "processing"
        and we have a transaction_id
        """
        order = mommy.prepare('order.Order',
                              status=Order.ORDER_STATUS.processing,
                              transaction_id='abc123ABC')

        subject = SendForPaymentService(order=order)
        self.assertTrue(subject.should_send_for_payment() is False)
