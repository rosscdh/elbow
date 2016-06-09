# -*- coding: UTF-8 -*-
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from elbow.utils import HTML2TextEmailMessageService

import logging
logger = logging.getLogger('django.request')


class SendEmailService(object):
    """
    Handle the sending of various email messages
    """
    required_project_docs = ['Verbraucherinformationsblatt',
                             'Finanzkennzahlen']

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
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']
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
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']
        logger.debug('Send founders email')

        msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, recipient_list)
        msg.attach_alternative(html2text.html, "text/html")

        if document.document:
            msg.attach_file(document.document.path)

        for doc in self.order.project.documents.filter(name__in=self.required_project_docs):
            if doc.document:
                msg.attach_file(doc.document.path)

        send_success.append(('founders', msg.send()))

        # Send Customer Email
        subject = _('TodayCapital.de - Your Investment Order has been created')
        message = html2text.plain_text
        from_email = 'application@todaycapital.de'

        for user in user_list:
            logger.debug('Send user %s email' % user)
            html2text = HTML2TextEmailMessageService(template_name='order/email/order_created_customer.html',
                                                     user=user,
                                                     order=self.order,
                                                     subject=subject)

            msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, [user.email])
            msg.attach_alternative(html2text.html, "text/html")

            if document:
                msg.attach_file(document.document.path)

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
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']
        logger.debug('Send founders email')
        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

        # Send Customer Email
        subject = _('TodayCapital.de - Investment Payment, Success')
        message = html2text.plain_text
        from_email = 'application@todaycapital.de'

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
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']

        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

        return send_success
