# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic import FormView, DetailView, View

from pinax.eventlog.models import log

from elbow.mixins import LoginRequiredMixin
from elbow.apps.project.models import Project

from .forms import CreateOrderForm, OrderMoreInfoForm, OrderLargeSumAgreementForm
from .models import Order


class OrderCreate(LoginRequiredMixin, FormView):
    project = None
    form_class = CreateOrderForm
    template_name = 'order/order-create.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        return super(OrderCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        self.order = form.save()
        self.order, payment_api_response = self.order.make_payment(user=self.request.user)
        return super(OrderCreate, self).form_valid(form=form)

    def get_success_url(self):
        return reverse('order:more_info', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

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


class OrderMoreInfo(LoginRequiredMixin, FormView):
    form_class = OrderMoreInfoForm
    template_name = 'order/order-moreinfo.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        self.order = Order.objects.get(uuid=self.kwargs.get('uuid'))
        return super(OrderMoreInfo, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderMoreInfo, self).get_context_data(*args, **kwargs)
        context.update({
            'project': self.project,
            'order': self.order,
        })
        return context

    def form_valid(self, form):
        self.order = form.save()
        return super(OrderMoreInfo, self).form_valid(form=form)

    def get_success_url(self):
        """
        If the user wants to pay more than 1k then by law they must sign and agree
        to the large sum agreement form terms
        """
        if self.order.amount.amount <= 1000:
            return reverse('order:payment', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})
        else:
            return reverse('order:large_sum_agreement', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})

    def get_form_kwargs(self):
        context = super(OrderMoreInfo, self).get_form_kwargs()
        context.update({
            'order': self.order,
            'user': self.request.user,
            'project': self.project,
            'data': self.request.POST if self.request.method.lower() in ['post'] else None,
        })
        return context


class OrderLargeSumAgreement(OrderMoreInfo):
    form_class = OrderLargeSumAgreementForm
    template_name = 'order/order-large_sum_agreement.html'

    def get_success_url(self):
        return reverse('order:payment', kwargs={'project_slug': self.project.slug, 'uuid': self.order.uuid})


class OrderPayment(LoginRequiredMixin, DetailView):
    template_name = 'order/order-payment.html'
    model = Order
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        return super(OrderPayment, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderPayment, self).get_context_data(*args, **kwargs)
        context.update({
            'project': self.project
        })
        return context


class OrderDetail(LoginRequiredMixin, DetailView):
    template_name = 'order/order-detail.html'
    model = Order
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'


class OrderWebhook(View):
    """
    Process payment webhooks
    """
    model = Order

    def get_object(self):
        return self.model.objects.get(transaction_id=self.transaction_id)

    def post(self, request, *args, **kwargs):
        self.transaction_id = request.POST.get('hash')
        try:
            order = self.get_object()
        except Order.DoesNotExist:
            order = None
            status_code = 400
            request.POST.update(ack='Disapproved',
                                error='Order with transaction_id of %s does not exist' % self.transaction_id)

        if order:
            amount = request.POST.get('amount')
            status_id = request.POST.get('status_id')
            status_description = request.POST.get('status_description')
            changed = request.POST.get('changed')
            apikey = request.POST.get('apikey')
            hint = request.POST.get('hint')
            payment_status = request.POST.get('payment_status')
            simplifiedstatus = request.POST.get('simplifiedstatus')

            log(
                user=request.user,
                action="order.lifecycle.payment.webhook.%s" % simplifiedstatus,
                obj=order,
                extra={
                    'transaction_id': self.transaction_id,
                    'amount': amount,
                    'status_id': status_id,
                    'status_description': status_description,
                    'changed': changed,
                    #'apikey': apikey, # Should not be TXing this at all
                    'hint': hint,
                    'payment_status': payment_status,
                    'simplifiedstatus': simplifiedstatus,
                }
            )
            status_code = 200
            request.POST.update(ack='Approved')

        content = request.POST.urlencode()

        return HttpResponse(content, 'text/plain', status_code)

