# -*- coding: UTF-8 -*-
from django.conf import settings
from django.core import mail
from django.core.urlresolvers import reverse
from elbow.apps.order.tests import BaseTestCase

from model_mommy import mommy


SIGNUP_DATA = {
    'first_name': 'Bob',
    'last_name': 'Tester',
    'email': 'test+user@example.com',
    'password1': 'test2007',
    'password2': 'test2007',
    'has_aggeed_t_and_c': True,
}


class EmailsSentOnNewSignupTest(BaseTestCase):
    """
    Test the right number of emails go out when a new user signs up
    """

    def setUp(self):
        super(EmailsSentOnNewSignupTest, self).setUp()
        mail.outbox = []

    def test_signup_sends_admin_email(self):
        url = reverse('account_signup')
        resp = self.c.post(url, SIGNUP_DATA)

        self.assertEqual(resp.status_code, 302)

        # # Should have email to managers and outgoing welcome email
        self.assertEqual(2, len(mail.outbox))

        email = mail.outbox[0]  # Admin Email
        self.assertEqual(unicode(email.subject), u'Registrieren')
        self.assertEqual(email.recipients(), ['post@todaycapital.de'])
        self.assertTrue('{base_url}/de/admin/auth/user/1/change'.format(base_url=settings.BASE_URL) in str(email.message()))

        email = mail.outbox[1]  # Customer Email
        self.assertEqual(email.subject, u'Registrierung abschlie\xdfen auf TodayCapital')
        self.assertEqual(email.recipients(), [u'test+user@example.com'])

