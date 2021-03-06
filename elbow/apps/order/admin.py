# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from django.http import JsonResponse
from django.template.response import TemplateResponse

from pinax.eventlog.models import log

from .models import Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project', 'tracking_number', 'payment_type', 'updated_at', 'status')
    list_filter = ('project','payment_type', 'status')
    search_fields = ('id', 'uuid', 'user__email', 'user__first_name', 'user__last_name', 'project__name', 'tracking_number', 'payment_type', 'status')

    def get_urls(self):
        urls = super(OrderAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<uuid>.*)/cancel/$',
                self.admin_site.admin_view(self.cancel_order),
                name='order_cancel'),

            url(r'^(?P<uuid>.*)/marked/reset/$',
                self.admin_site.admin_view(self.reset_order),
                name='order_reset'),

            url(r'^(?P<uuid>.*)/marked/paid/$',
                self.admin_site.admin_view(self.marked_as_paid),
                name='order_marked_as_paid'),

            url(r'^(?P<uuid>.*)/log/$',
                self.admin_site.admin_view(self.log_event),
                name='order_logs'),
        ]
        return my_urls + urls

    def get_order(self, uuid):
        return Order.objects.get(uuid=uuid)

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

    def reset_order(self, request, uuid):
        order = self.get_order(uuid=uuid)
        order.status = order.ORDER_STATUS.created
        order.save(update_fields=['status'])

        log(
            user=request.user,
            action="order.lifecycle.reset",
            obj=order,
            extra={
                "note": "%s Reset the Order" % request.user
            }
        )
        resp = {}
        return JsonResponse(resp)

    def marked_as_paid(self, request, uuid):
        order = self.get_order(uuid=uuid)
        order.status = order.ORDER_STATUS.paid_manually
        order.save(update_fields=['status'])

        log(
            user=request.user,
            action="order.lifecycle.manually_marked_as_piad",
            obj=order,
            extra={
                "note": "%s Marked the Order as manually paid" % request.user
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
        else:
            resp = {
                'is_popup': True,
                'order': order,
                'object_list': order.log_history,
            }
            return TemplateResponse(request,
                                    'order/admin/order-logs.html',
                                    resp)


admin.site.register(Order, OrderAdmin)
