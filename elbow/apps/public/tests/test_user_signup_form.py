# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse
from elbow.apps.order.tests import BaseTestCase


class SignupCreatesUserProfileTest(BaseTestCase):
    """
    Test that the SignUpForm has the right stuff
    """
    def test_signup_form_shows_corect_fields(self):
        url = reverse('account_signup')
        resp = self.c.get(url)

        self.assertEqual(resp.status_code, 200)
        form = resp.context['form']
        self.assertEqual(form.__class__.__name__, 'SignUpForm')
        self.assertEqual(form.fields.keys(), ['email',
                                              'password1',
                                              'password2',
                                              'confirmation_key',
                                              'has_aggeed_t_and_c',
                                              'send_news_and_info'])
