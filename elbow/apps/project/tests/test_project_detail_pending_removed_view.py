# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse
from elbow.apps.project.models import Project
from model_mommy import mommy

from elbow.apps.order.tests import BaseTestCase


class ProjectStatusPendingOrRemovedTest(BaseTestCase):
    """
    Test that if the redirect_url field has a value then we are redirected there
    """
    def setUp(self):
        super(ProjectStatusPendingOrRemovedTest, self).setUp()
        self.project = mommy.make('project.Project',
                                  name='My Basic Test Project',
                                  status=Project.PROJECT_STATUS.active)

        self.detail_url = reverse('project:detail', kwargs={'slug': self.project.slug})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

    def test_project_shows_404_if_pending(self):
        """
        Should not show if status pending
        """
        self.project.status = self.project.PROJECT_STATUS.pending
        self.project.save(update_fields=['status'])

        resp = self.c.get(self.detail_url)
        self.assertEqual(resp.status_code, 404)

    def test_project_shows_404_if_removed(self):
        """
        Should not show if status pending
        """
        self.project.status = self.project.PROJECT_STATUS.removed
        self.project.save(update_fields=['status'])

        resp = self.c.get(self.detail_url)
        self.assertEqual(resp.status_code, 404)