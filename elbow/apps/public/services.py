# -*- coding: UTF-8 -*-
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _
from django.core.mail import send_mail, EmailMultiAlternatives

from elbow.utils import HTML2TextEmailMessageService

import logging
logger = logging.getLogger('django.request')


class SendEmailService(object):
    """
    Handle the sending of various email messages
    """
    required_project_docs = ['Verbraucherinformationsblatt',
                             'Finanzkennzahlen']
    admin_recipient_list = ['post@todaycapital.de']

    def __init__(self, order, **kwargs):
        self.order = order
        self._messages = []

    @staticmethod
    def send_user_signedup_admin_email(user_list):
        logger.debug('Order Created')
        send_success = []
        subject = _('TodayCapital.de - New sign-up')

        html2text = HTML2TextEmailMessageService(template_name='public/email/send_user_signedup_admin.html',
                                                 recipients=user_list,
                                                 subject=subject)
        # Send Admin Email
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'
        recipient_list = SendEmailService.admin_recipient_list
        logger.debug('Send founders email')
        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

    def send_order_created_email(self, user_list):
        logger.debug('Order Created')
        send_success = []
        document = self.order.documents.filter(document_type='order',
                                               user=self.order.user)  \
                                       .order_by('-id').first()

        subject = _('TodayCapital.de - a new order has been created')
        html2text = HTML2TextEmailMessageService(template_name='order/email/order_created.html',
                                                 order=self.order,
                                                 recipients=user_list,
                                                 subject=subject)
        # Send Admin Email
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'
        recipient_list = self.admin_recipient_list
        logger.debug('Send founders email')

        msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, recipient_list)
        msg.attach_alternative(html2text.html, "text/html")

        if document.document:
            file_name = '%s.pdf' % slugify('%s-%s-%s' % (_('Loan Agreement'), self.order.project.name, self.order.tracking_number))
            msg.attach(filename=file_name, content=document.document.read(), mimetype='application/pdf')

        for doc in self.order.project.documents.filter(name__in=self.required_project_docs):
            if doc.document:
                msg.attach_file(doc.document.path)

        send_success.append(('founders', msg.send()))

        # Send Customer Email
        subject = _('TodayCapital.de - Your Investment Order has been created')
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'

        for user in user_list:
            logger.debug('Send user %s email' % user)

            template_name = None
            if self.order.payment_type == self.order.ORDER_PAYMENT_TYPE.debit:
                template_name = 'order/email/order_created_customer_debit.html'

            if self.order.payment_type == self.order.ORDER_PAYMENT_TYPE.prepay:
                template_name = 'order/email/order_created_customer_prepay.html'

            if template_name is None:
                raise Exception('Could not identify customer email template based on order.payment_type: %s' % order.payment_type)

            html2text = HTML2TextEmailMessageService(template_name=template_name,
                                                     user=user,
                                                     order=self.order,
                                                     subject=subject)

            msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, [user.email])
            msg.attach_alternative(html2text.html, "text/html")

            if document:
                file_name = '%s.pdf' % slugify('%s-%s-%s' % (_('Loan Agreement'), self.order.project.name, self.order.tracking_number))
                msg.attach(filename=file_name, content=document.document.read(), mimetype='application/pdf')

            send_success.append(('customer', msg.send()))

        return send_success

    def send_success_email(self, user_list):
        logger.debug('Payment Success')
        send_success = []

        subject = _('TodayCapital.de - [admin] Investment Payment, Success')
        html2text = HTML2TextEmailMessageService(template_name='order/email/payment_admin_success.html',
                                                 order=self.order,
                                                 recipients=user_list,
                                                 subject=subject)
        # Send Admin Email
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'
        recipient_list = self.admin_recipient_list
        logger.debug('Send founders email')
        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

        # Send Customer Email
        subject = _('TodayCapital.de - Investment Payment, Success')
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'

        for user in user_list:
            logger.debug('Send user %s email' % user)
            html2text = HTML2TextEmailMessageService(template_name='order/email/payment_customer_success.html',
                                                     user=user,
                                                     order=self.order,
                                                     subject=subject)

            send_success.append(('customer', send_mail(subject=subject,
                                                       message=message,
                                                       from_email=from_email,
                                                       recipient_list=[user.email],
                                                       html_message=html2text.html)))
        return send_success

    def send_fail_email(self):
        """
        Was decided to send fail email to founders only, so that they can starta  conversation with the invstor
        """
        logger.debug('Payment Failure')
        send_success = []

        subject = _('TodayCapital.de - [admin] Investment Payment, Failure')
        html2text = HTML2TextEmailMessageService(template_name='order/email/payment_admin_fail.html',
                                                 order=self.order,
                                                 subject=subject)

        # Send Customer Email
        message = html2text.plain_text
        from_email = 'noreply@todaycapital.de'
        recipient_list = self.admin_recipient_list

        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

        return send_success
