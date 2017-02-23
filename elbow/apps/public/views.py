# -*- coding: utf-8 -*-
from django.views.generic import RedirectView
from allauth.account.views import LoginView as AllAuthLoginView
from allauth.account.views import SignupView as AllAuthSignupView

from elbow.apps.project.models import Project
from elbow.mixins import LoginRequiredMixin


#class HomePageView(TemplateView):
class HomePageView(LoginRequiredMixin, RedirectView):
    #url = '/de/p/start/'
    url = '/de/orders/todayhaus/order/'
    template_name = 'home/home.html'

    def get_context_data(self):
        context = super(HomePageView, self).get_context_data()
        context.update({
            'project_list': Project.objects.public()
        })
        return context


class LoginView(AllAuthLoginView):
    pass


class SignupView(AllAuthSignupView):
    pass
