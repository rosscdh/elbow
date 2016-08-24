# -*- coding: utf-8 -*-
from django.http import FileResponse
from django.views.generic import DetailView

from elbow.mixins import LoginRequiredMixin
from elbow.apps.order.apps import SECUPAY_BANK_DATA

from .models import Document


class DocumentDownload(LoginRequiredMixin, DetailView):
    template_name = 'order/order-payment.html'
    model = Document
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'
    content_type = 'application/pdf'

    def get_context_data(self, **kwargs):
        kwargs = super(DocumentDownload, self).get_context_data(**kwargs)
        kwargs.update({
            'SECUPAY_BANK_DATA': SECUPAY_BANK_DATA,
        })
        return kwargs

    def render_to_response(self, *args, **kwargs):
        return FileResponse(self.get_object().document, content_type=self.content_type)
