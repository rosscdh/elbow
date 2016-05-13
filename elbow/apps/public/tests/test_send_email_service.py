# -*- coding: UTF-8 -*-
from django.core import mail
from elbow.apps.order.tests import BaseTestCase

from model_mommy import mommy
from elbow.apps.order.models import Order
from elbow.apps.public.services import SendEmailService


class SendForPaymentEmailServiceTest(BaseTestCase):
    """
    UnitTest the service methods, with a VALID order object
    """

    def setUp(self):
        super(SendForPaymentEmailServiceTest, self).setUp()
        mail.outbox = []
        self.order = mommy.prepare('order.Order',
                                   status=Order.ORDER_STATUS.processing,  # Must be in processing
                                   transaction_id=None)  # AND must NOT have a transaction_id
        self.order.user.email = 'bob@example.com'  # Set the email of the order User

        self.subject = SendEmailService(order=self.order)

    def test_required_project_docs(self):
        self.assertEqual(self.subject.required_project_docs, ['Verbraucherinformationsblatt',
                                                              'Finanzkennzahlen'])

    def test_send_success_email(self):
        result = self.subject.send_success_email(user_list=[self.order.user])  # Send the email
        # Should have email to managers AND email to customer
        self.assertEqual(2, len(mail.outbox))
        self.assertEqual(type(result), list)
        self.assertEqual(result, [('founders', 1), ('customer', 1)])

        for email in mail.outbox:
            self.assertEqual(unicode(email.subject), u'TodayCapital.de - Ihre Zahlung ist eingegangen')

        email = mail.outbox[0]  # 0 should be to the Founders
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])

        email = mail.outbox[1]  # 1 should be to the Customers
        self.assertEqual(email.recipients(), [self.order.user.email])

    def test_send_fail_email(self):
        result = self.subject.send_fail_email()  # Send the email
        # Should have email to managers ONLY
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(type(result), list)
        self.assertEqual(result, [('founders', 1)])
        email = mail.outbox[0]
        self.assertEqual(unicode(email.subject), 'TodayCapital.de - Offener Zahlungseingang zu Ihrem Investment')
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])

