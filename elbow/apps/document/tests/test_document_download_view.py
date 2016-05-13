# -*- coding: UTF-8 -*-
from elbow.apps.order.tests import BaseTestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy


class DocumentDownloadViewTest(BaseTestCase):
    """
    Test basic view flow
    """
    def setUp(self):
        super(DocumentDownloadViewTest, self).setUp()
        self.document = mommy.make('document.Document')
        self.url = reverse('document:download', kwargs={'uuid': self.document.uuid})

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

    def test_unauthenticated_redirects_to_login(self):
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, u'/accounts/login/?next=/de/documents/%s/download/' % self.document.uuid)


    def test_downloads_to_authenticated(self):
        self.c.force_login(self.user)
        resp = self.c.get(self.url)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.__class__.__name__, 'FileResponse')
        self.assertEqual(resp.items(), [('Vary', 'Accept-Encoding, Cookie'),
                                        ('Content-Type', 'application/pdf'),
                                        ('Content-Language', 'de')])
