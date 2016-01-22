# -*- coding: utf-8 -*-
from django.views.generic import FormView, DetailView

from elbow.mixins import LoginRequiredMixin
from elbow.apps.project.models import Project

from .forms import CreateOrderForm
from .models import Order


class OrderCreate(LoginRequiredMixin, FormView):
    project = None
    template_name = 'order/order-create.html'
    form_class = CreateOrderForm

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        return super(OrderCreate, self).dispatch(request, *args, **kwargs)

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, *args, **kwargs):
        context = super(OrderCreate, self).get_context_data(*args, **kwargs)
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
