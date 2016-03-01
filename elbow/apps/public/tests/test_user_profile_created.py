# -*- coding: UTF-8 -*-
from django.core import mail
from django.core.urlresolvers import reverse
from elbow.apps.order.tests import BaseTestCase

from django.contrib.auth import get_user_model


SIGNUP_DATA = {
    'email': 'test+user@example.com',
    'password1': 'test2007',
    'password2': 'test2007',
    'has_aggeed_t_and_c': 'on',
}


class SignupCreatesUserProfileTest(BaseTestCase):
    """
    Test that when the user signs up the user profile object is created
    """
    def test_signup_creates_user_profile(self):
        url = reverse('account_signup')
        resp = self.c.post(url, SIGNUP_DATA)

        self.assertEqual(resp.status_code, 302)

        user = get_user_model().objects.get(email=SIGNUP_DATA.get('email'))
        # Test we have a user profile
        self.assertEqual(user.userprofile.__class__.__name__, 'UserProfile')
        # Test it has data
        self.assertEqual(user.userprofile.data, {
            u'has_aggeed_t_and_c': u'on',
            u'send_news_and_info': None
        })
