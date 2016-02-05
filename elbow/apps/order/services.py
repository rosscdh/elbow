# -*- coding: UTF-8 -*-
from django.core.files.base import ContentFile

from easy_pdf.rendering import render_to_pdf

from elbow.apps.public.services import SendEmailService
from elbow.apps.document.models import Document, _document_upload_path

import logging
logger = logging.getLogger('django.request')


class SendForPaymentService(object):
    """
    Handle the sending of the order for payment processing
    or not
    """
    def __init__(self, order, **kwargs):
        self.order = order
        self._messages = []
        self.email_service = SendEmailService(order=order)

    def should_send_for_payment(self):
        """
        In order to be sent to secupay, we must be in "processing" status AND have a None for transaction_id
        """
        return self.order.can_send_payment

    def send_payment(self):
        return {}

    def process(self):
        if self.should_send_for_payment() is True:
            logger.debug('Attempting to send Payment')
            if self.send_payment():
                self.email_service.send_success_email()
            else:
                self.email_service.send_fail_email()
        else:
            self._messages.push({'type': 'error', 'title': 'Can not be sent for payment.', 'message': ''})
            logger.debug('Is not valid and should not be sent for payment')


class CreateMoreInfoAgreementPDFService(object):
    def __init__(self, order, user, **kwargs):
        self.order = order
        self.user = user

    def process(self, **kwargs):
        kwargs.update({
            'order': self.order,
            'project': self.order.project,
            'user': self.user
        })

        pdf_bytes = render_to_pdf(template='order/documents/more_info_agreement.html',
                                  context=kwargs,
                                  encoding=u'utf-8')

        doc = Document(name='More Info Agreement - %s and %s' % (self.order.uuid, self.order.customer_name),
                       document_type=Document.DOCUMENT_TYPES.order)
        #doc.document.save('test.pdf', ContentFile(pdf_bytes))
        doc.document.save(_document_upload_path(doc, 'info-agreement.pdf'), ContentFile(pdf_bytes))
        doc.save()
        self.order.documents.add(doc)
        return self.order
