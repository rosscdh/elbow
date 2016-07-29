# -*- coding: utf-8 -*-
#from django.views.generic import TemplateView
from django.views.generic import RedirectView
from elbow.apps.project.models import Project


#class HomePageView(TemplateView):
class HomePageView(RedirectView):
    url = '/de/p/start/'
    template_name = 'home/home.html'

    def get_context_data(self):
        context = super(HomePageView, self).get_context_data()
        context.update({
            'project_list': Project.objects.public()
        })
        return context
