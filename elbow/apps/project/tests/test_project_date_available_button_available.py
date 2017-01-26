# -*- coding: UTF-8 -*-
import datetime
from django.core.urlresolvers import reverse

from model_mommy import mommy

from elbow.apps.order.tests import BaseTestCase


class ProjectDateAvailableBase(BaseTestCase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    def setUp(self):
        super(ProjectDateAvailableBase, self).setUp()
        assert hasattr(self, 'date_available'), 'Define a date_available for this test class'

        self.project = mommy.make('project.Project',
                                  name='My Basic Test Project',
                                  date_available=self.date_available)

        self.detail_url = reverse('project:detail', kwargs={'slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)
        self.c.force_login(self.user)


class ProjectDateAvailableButtonTest(ProjectDateAvailableBase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    date_available = datetime.datetime.today() + datetime.timedelta(days=1)

    def test_is_available_for_investment(self):
        self.assertEqual(self.project.is_available_for_investment, False)

    def test_is_view_shows_message_and_coming_soon_button(self):
        """
        Should not redirect if no redirect_url is set
        """
        resp = self.c.get(self.project.invest_now_url)
        self.assertTrue('not-yet-available' in resp.content)
        self.assertTrue('m\xc3\xb6glich ab' in resp.content)


class ProjectDateIsAvailableButtonTest(ProjectDateAvailableBase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    date_available = datetime.datetime.today()

    def test_is_available_for_investment(self):
        self.assertEqual(self.project.is_available_for_investment, True)

    def test_is_view_shows_message_and_coming_soon_button(self):
        """
        Should not redirect if no redirect_url is set
        """
        resp = self.c.get(self.project.invest_now_url)
        self.assertTrue('not-yet-available' not in resp.content)
        self.assertTrue('m\xc3\xb6glich ab' not in resp.content)


class ProjectDateIsAvailableWithNoDateDefinedButtonTest(ProjectDateAvailableBase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    date_available = None

    def test_is_available_for_investment(self):
        self.assertEqual(self.project.is_available_for_investment, True)

    def test_is_view_shows_message_and_coming_soon_button(self):
        """
        Should not redirect if no redirect_url is set
        """
        resp = self.c.get(self.project.invest_now_url)
        self.assertTrue('not-yet-available' not in resp.content)
        self.assertTrue('m\xc3\xb6glich ab' not in resp.content)