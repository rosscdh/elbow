# -*- coding: utf-8 -*-
#from django.views.generic import TemplateView
from django.views.generic import RedirectView
from django.core.urlresolvers import reverse

from elbow.apps.document.models import Document
from elbow.apps.project.models import Project


class PDFPermalinkView(RedirectView):
    def get_object(self):
        return Project.objects.get(slug=self.kwargs.get('slug'))

    def get_redirect_url(self, *args, **kwargs):
        media_slug = self.kwargs.get('media_slug')
        project = self.get_object()
        document = None

        if media_slug in ['term-sheet', 'loan-agreement']:
            login_required = True
        else:
            document = Document.objects.get(uuid=media_slug)
            login_required = document.login_required

        # Get the url
        if document is None:
            # we have a hardcoded file
            if media_slug == 'term-sheet':
                url = project.term_sheet_doc.url
            elif media_slug == 'loan-agreement':
                url = project.loan_agreement_doc.url
        else:
            # is a standard document so get its url
            url = document.url

        if login_required is True:
            # if authenticated
            if self.request.user.is_authenticated() is True:
                return url
            else:
                # not autenticated
                return reverse('account_login')
        return url
