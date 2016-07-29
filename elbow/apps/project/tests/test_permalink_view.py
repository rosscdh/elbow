# -*- coding: UTF-8 -*-
from django.core.urlresolvers import reverse
from django.core.files.base import ContentFile

from model_mommy import mommy

from elbow.apps.order.tests import BaseTestCase



class ProjectDocumentPermalinkTest(BaseTestCase):
    """
    Test the permalink view
    """
    def setUp(self):
        super(ProjectDocumentPermalinkTest, self).setUp()
        self.project = mommy.make('project.Project',
                                  name='My Basic Test Project')
        self.project.term_sheet_doc.save('test_term_sheet_doc.pdf', ContentFile('test term_sheet_doc'), save=False)
        self.project.loan_agreement_doc.save('test_loan_agreement_doc.pdf', ContentFile('test loan_agreement_doc'), save=False)
        self.project.save()

        self.project.documents = mommy.make('document.Document', _quantity=3)

        user_dict = {'first_name': 'Test', 'last_name': 'User', 'email': 'test@example.com'}
        self.user = mommy.make('auth.User', **user_dict)

    def test_project_term_sheet_doc_permalink(self):
        """
        Autoslug should auto generate the slug field
        """
        self.assertEqual(self.project.term_sheet_doc_permalink, u'/de/projects/my-basic-test-project/media/term-sheet/permalink/')

    def test_project_loan_agreement_doc_permalink(self):
        """
        Autoslug should auto generate the slug field
        """
        self.assertEqual(self.project.loan_agreement_doc_permalink, u'/de/projects/my-basic-test-project/media/loan-agreement/permalink/')

    def test_authentication_required_redirect(self):
        resp = self.c.get(reverse('project:media_permalink', kwargs={'slug':self.project.slug, 'media_slug': 'term-sheet'}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/accounts/login/')

        resp = self.c.get(reverse('project:media_permalink', kwargs={'slug':self.project.slug, 'media_slug': 'loan-agreement'}))
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, '/de/accounts/login/')

    def test_authentication_required_redirect(self):
        self.c.force_login(self.user)

        resp = self.c.get(reverse('project:media_permalink', kwargs={'slug':self.project.slug, 'media_slug': 'term-sheet'}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue('/media/project/my-basic-test-project/doc-test_term_sheet_doc_' in resp.url)

        resp = self.c.get(reverse('project:media_permalink', kwargs={'slug':self.project.slug, 'media_slug': 'loan-agreement'}))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue('/media/project/my-basic-test-project/doc-test_loan_agreement_doc_' in resp.url)

    def test_not_existing_document_throws_404(self):
        self.c.force_login(self.user)
        resp = self.c.get(reverse('project:media_permalink', kwargs={'slug':self.project.slug, 'media_slug': 'monkey-bum'}))
        self.assertEqual(resp.status_code, 404)
