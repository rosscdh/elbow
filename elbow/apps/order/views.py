# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.defaultfilters import slugify
from django.views.generic import FormView, ListView, DetailView, View

from pinax.eventlog.models import log

from elbow.mixins import LoginRequiredMixin
from elbow.apps.project.models import Project

from .forms import CreateOrderForm, OrderLoanAgreementForm
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
        try:
            self.order, payment_api_response = self.order.make_payment(user=self.request.user)
        except Exception as e:
            log(
                user=self.request.user,
                action="order.lifecycle.payment.attempt.failed",
                obj=self.order,
                extra={
                    'order.make_payment failed'
                    'error': unicode(e),
                }
            )
            # Raise so that rollbar catches it and alerts us
            raise e

        return super(OrderCreate, self).form_valid(form=form)

    def get_success_url(self):
        return self.order.url

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


class OrderLoanAgreementView(FormView):
    form_class = OrderLoanAgreementForm
    template_name = 'order/order-loan_agreement.html'

    def dispatch(self, request, *args, **kwargs):
        self.project = Project.objects.get(slug=self.kwargs.get('project_slug'))
        self.order = Order.objects.get(uuid=self.kwargs.get('uuid'))
        return super(OrderLoanAgreementView, self).dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        context = super(OrderLoanAgreementView, self).get_form_kwargs()
        context.update({
            'order': self.order,
            'user': self.request.user,
            'project': self.project,
            'data': self.request.POST if self.request.method.lower() in ['post'] else None,
        })
        return context

    def form_valid(self, form):
        self.order = form.save()
        return super(OrderLoanAgreementView, self).form_valid(form=form)

    def get_context_data(self, *args, **kwargs):
        context = super(OrderLoanAgreementView, self).get_context_data(*args, **kwargs)
        context.update({
            'project': self.project,
            'order': self.order,
            'document': self.order.documents.filter(user=self.order.user).first(),
        })
        return context

    def get_success_url(self):
        """
        If the user wants to pay more than 1k then by law they must sign and agree
        to the large sum agreement form terms
        """
        #
        # model does url resolving
        #
        return self.order.url

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


class UserOrderList(LoginRequiredMixin, ListView):
    template_name = 'order/order-list.html'
    model = Order
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


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
        data = request.POST.copy()
        self.transaction_id = request.POST.get('hash')

        try:
            order = self.get_object()
        except Order.DoesNotExist:
            order = None
            status_code = 400
            data.update(ack='Disapproved',
                        error='Order with transaction_id of %s does not exist' % self.transaction_id)

        if order:
            amount = request.POST.get('amount')
            status_id = request.POST.get('status_id')
            status_description = request.POST.get('status_description')
            changed = request.POST.get('changed')
            #apikey = request.POST.get('apikey')
            hint = request.POST.get('hint')
            payment_status = request.POST.get('payment_status')
            #extended_status_description = order.SECUPAY.status_id_description(status_id=status_id)
            simplifiedstatus = request.POST.get('simplifiedstatus')

            log(
                user=request.user,
                action="order.lifecycle.payment.webhook.%s" % slugify(payment_status),
                obj=order,
                extra={
                    'transaction_id': self.transaction_id,
                    'amount': amount,
                    'status_id': status_id,
                    'status_description': status_description,
                    'changed': changed,
                    #  'apikey': apikey, # Should not be TXing this at all
                    'hint': hint,
                    'payment_status': payment_status,
                    'simplifiedstatus': simplifiedstatus,
                    #'extended_status_description': extended_status_description,
                    #  'simplifiedstatus': simplifiedstatus, # Is not provided by api?
                }
            )
            status_code = 200
            data.update(ack='Approved')  # Sigh.. no not necessariy approved but secupay needs this

            #
            # update the order details
            #
            if payment_status in ['accepted']:
                order.status = order.ORDER_STATUS.paid

            if payment_status in ['authorized'] \
               and order.payment_type == order.ORDER_PAYMENT_TYPE.debit:
                #
                # IN the case of an authorized event (bank has allwed the tx)
                # we need to manually capture the payment
                #
                order.capture_authorized_payment(user=request.user)
            #
            # Handle updating of info in data field
            #
            order.data['payment_status_description'] = status_description
            #order.data['payment_extended_status_description'] = extended_status_description
            order.save()

        #
        # re-urlencode the data for presentation back to secupay
        #
        content = data.urlencode()

        return HttpResponse(content, 'text/plain', status_code)

