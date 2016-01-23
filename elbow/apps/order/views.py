# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
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

    def form_valid(self, form):
        self.order = form.save()
        return super(OrderCreate, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('order:payment', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

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
            'data': self.request.POST if self.request.method.lower() in ['post'] else None,
        }


class OrderPayment(LoginRequiredMixin, DetailView):
    template_name = 'order/order-payment.html'
    model = Order

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        return super(OrderPayment, self).dispatch(request, *args, **kwargs)


class OrderDetail(LoginRequiredMixin, DetailView):
    template_name = 'order/order-detail.html'
    model = Order
