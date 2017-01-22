# -*- coding: utf-8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, RedirectView
from django.core.urlresolvers import reverse

from elbow.apps.project.models import Project


class ProjectDetailView(DetailView):
    model = Project
    template_name = 'project/project-detail.html'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        #
        # If a redirect url is set then redirect
        #
        if self.object.redirect_url:
            return HttpResponseRedirect(self.object.redirect_url)

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


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
            #
            # Get the document object
            #
            document = get_object_or_404(project.documents, uuid=media_slug)
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
            url = document.document.url

        if login_required is True:
            # if authenticated
            if self.request.user.is_authenticated() is True:
                return url
            else:
                # not autenticated
                return reverse('account_login')

        return url
