# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from django.http import JsonResponse

from pinax.eventlog.models import log

from .models import Order
from .services import SendForPaymentService


class OrderAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super(OrderAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<uuid>.*)/send/$',
                self.admin_site.admin_view(self.send_for_payment),
                name='order_send_for_payment'),

            url(r'^(?P<uuid>.*)/cancel/$',
                self.admin_site.admin_view(self.cancel_order),
                name='order_cancel'),

            url(r'^(?P<uuid>.*)/log/$',
                self.admin_site.admin_view(self.log_event),
                name='order_add_log'),
        ]
        return my_urls + urls

    def get_order(self, uuid):
        return Order.objects.get(uuid=uuid)

    def send_for_payment(self, request, uuid):
        order = self.get_order(uuid=uuid)

        order.status = order.ORDER_STATUS.processing
        order.save(update_fields=['status'])

        service = SendForPaymentService(order=order)
        service.process()
        log(
            user=request.user,
            action="order.lifecycle.sent_for_payment",
            obj=order,
            extra={
                "note": "%s Sent the Order to secupay for payment" % request.user
            }
        )
        resp = {}
        return JsonResponse(resp)

    def cancel_order(self, request, uuid):
        order = self.get_order(uuid=uuid)

        order.status = order.ORDER_STATUS.cancelled
        order.save(update_fields=['status'])

        log(
            user=request.user,
            action="order.lifecycle.cancelled",
            obj=order,
            extra={
                "note": "%s Cancelled the Order" % request.user
            }
        )
        resp = {}
        return JsonResponse(resp)

    def log_event(self, request, uuid):
        order = self.get_order(uuid=uuid)
        resp = {}

        if request.method == 'POST':
            log(
                user=request.user,
                action="order.note.add",
                obj=order,
                extra={
                    "note": request.POST.get('note')
                }
            )

        return JsonResponse(resp)

admin.site.register(Order, OrderAdmin)
