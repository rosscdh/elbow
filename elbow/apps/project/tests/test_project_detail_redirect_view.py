# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse

from model_mommy import mommy

from elbow.apps.order.tests import BaseTestCase
from elbow.apps.project.models import Project


class ProjectDocumentRedirectUrlTest(BaseTestCase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    def setUp(self):
        super(ProjectDocumentRedirectUrlTest, self).setUp()
        self.project = mommy.make('project.Project',
                                  name='My Basic Test Project',
                                  status=Project.PROJECT_STATUS.active,
                                  redirect_url=None)

        self.detail_url = reverse('project:detail', kwargs={'slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

    def test_project_does_not_redirect_if_no_value(self):
        """
        Should not redirect if no redirect_url is set
        """
        self.project.redirect_url = None
        self.project.save(update_fields=['redirect_url'])
        resp = self.c.get(self.detail_url)
        self.assertEqual(resp.status_code, 200)

    def test_project_does_redirect_if_redirect_url_present(self):
        """
        Should not redirect if no redirect_url is set
        """
        self.project.redirect_url = 'https://google.com/'
        self.project.save(update_fields=['redirect_url'])
        resp = self.c.get(self.detail_url)
        self.assertEqual(resp.status_code, 302)

