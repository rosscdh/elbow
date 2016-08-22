# -*- coding: UTF-8 -*-
from django.core.files.base import ContentFile
from django.utils.translation import ugettext_lazy as _

from easy_pdf.rendering import render_to_pdf

from elbow.apps.document.models import Document, _document_upload_path
from elbow.apps.order.apps import SECUPAY_BANK_DATA

import logging
logger = logging.getLogger('django.request')


class LoanAgreementCreatePDFService(object):
    """
    Service that creates the more info agreement
    """
    def __init__(self, order, user, **kwargs):
        self.order = order
        self.user = user

    def process(self, **kwargs):
        kwargs.update({
            'order': self.order,
            'project': self.order.project,
            'user': self.user,
            'SECUPAY_BANK_DATA': SECUPAY_BANK_DATA,
        })

        pdf_bytes = render_to_pdf(template='order/documents/loan_agreement.html',
                                  context=kwargs,
                                  encoding=u'utf-8')

        doc = Document(name='%s - %s' % (_('Loan Agreement'), self.order.customer_name),
                       document_type=Document.DOCUMENT_TYPES.order,
                       user=self.user)

        doc.document.save(_document_upload_path(doc, _('loan-agreement.pdf')),
                          ContentFile(pdf_bytes))
        doc.save()

        self.order.documents.add(doc)

        return self.order
