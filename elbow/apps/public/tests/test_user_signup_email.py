# -*- coding: UTF-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from elbow.apps.order.tests import BaseTestCase

from model_mommy import mommy


SIGNUP_DATA = {
    'email': 'test+user@example.com',
    'password1': 'test2007',
    'password2': 'test2007',
}


class SendForPaymentEmailServiceTest(BaseTestCase):
    """
    UnitTest the service methods, with a VALID order object
    """

    def setUp(self):
        super(SendForPaymentEmailServiceTest, self).setUp()
        mail.outbox = []

    def test_signup_sends_admin_email(self):
        url = reverse('account_signup')
        resp = self.c.post(url, SIGNUP_DATA)

        self.assertEqual(resp.status_code, 302)

        # # Should have email to managers and outgoing welcome email
        self.assertEqual(2, len(mail.outbox))

        email = mail.outbox[0]  # Admin Email
        self.assertEqual(unicode(email.subject), 'TodayCapital.de - New sign-up')
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])


        email = mail.outbox[1]  # Customer Email
        self.assertEqual(email.subject, '[example.com] Please Confirm Your E-mail Address')
        self.assertEqual(email.recipients(), [u'test+user@example.com'])

