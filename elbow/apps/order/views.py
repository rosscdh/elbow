# -*- coding: utf-8 -*-
from django.views.generic import CreateView, DetailView

from elbow.mixins import LoginRequiredMixin
from elbow.apps.project.models import Project

from .forms import CreateOrderForm
from .models import Order


class OrderCreate(LoginRequiredMixin, CreateView):
    project = None
    template_name = 'order/order-create.html'
    form_class = CreateOrderForm

    def get_context_data(self):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        context = super(OrderCreate, self).get_context_data()
        context.update({
            'project': self.project
        })
        return context

    def get_form_kwargs(self):
        return {
            'user': self.request.user,
            'project': self.project,
        }


class OrderDetail(LoginRequiredMixin, DetailView):
    template_name = 'order/order-detail.html'
    model = Order
