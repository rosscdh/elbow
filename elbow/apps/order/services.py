# -*- coding: UTF-8 -*-
from django.core.files.base import ContentFile

from easy_pdf.rendering import render_to_pdf

from elbow.apps.public.services import SendEmailService
from elbow.apps.document.models import Document, _document_upload_path

import logging
logger = logging.getLogger('django.request')



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
