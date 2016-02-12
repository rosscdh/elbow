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
    def __init__(self, order, **kwargs):
        self.order = order
        self._messages = []

    def send_order_created_email(self, user_list):
        logger.debug('Order Created')
        send_success = []
        html2text = HTML2TextEmailMessageService(template_name='order/email/order_created.html',
                                                 order=self.order,
                                                 recipients=user_list)
        # Send Admin Email
        subject = _('TodayCapital.de - Investment order created')
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
        subject = _('TodayCapital.de - Your Investment Order has been created')
        message = html2text.plain_text
        from_email = 'application@todaycapital.de'

        for user in user_list:
            logger.debug('Send user %s email' % user)
            html2text = HTML2TextEmailMessageService(template_name='order/email/order_created_customer.html',
                                                     user=user,
                                                     order=self.order)

            send_success.append(('customer', send_mail(subject=subject,
                                                       message=message,
                                                       from_email=from_email,
                                                       recipient_list=[user.email],
                                                       html_message=html2text.html)))
        return send_success

    def send_order_loan_agreement_email(self, user_list):
        logger.debug('Order More Info')
        send_success = []

        document = self.order.documents.filter(document_type='order',
                                               user=self.order.user)  \
                                       .order_by('-id').first()
        #import pdb;pdb.set_trace()
        html2text = HTML2TextEmailMessageService(template_name='order/email/order_more_info.html',
                                                 order=self.order,
                                                 recipients=user_list)
        # Send Admin Email
        subject = _('TodayCapital.de - Investment order provided more information')
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']

        logger.debug('Send founders email')

        msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, recipient_list)
        msg.attach_alternative(html2text.html, "text/html")

        if document:
            msg.attach_file(document.document.path)

        send_success.append(('founders', msg.send()))

        # Send Customer Email
        subject = _('TodayCapital.de - Your Investment Order Info, Attached Agreement')
        from_email = 'application@todaycapital.de'

        for user in user_list:
            logger.debug('Send user %s email' % user)
            html2text = HTML2TextEmailMessageService(template_name='order/email/order_more_info_customer.html',
                                                     user=user,
                                                     order=self.order)

            msg = EmailMultiAlternatives(subject, html2text.plain_text, from_email, [user.email])
            msg.attach_alternative(html2text.html, "text/html")
            if document:
                msg.attach_file(document.document.path)

            send_success.append(('customer', msg.send()))

        return send_success

    def send_success_email(self, user_list):
        logger.debug('Payment Success')
        send_success = []
        html2text = HTML2TextEmailMessageService(template_name='order/email/payment_admin_success.html',
                                                 order=self.order,
                                                 recipients=user_list)
        # Send Admin Email
        subject = _('TodayCapital.de - Investment Payment, Success')
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
                                                     order=self.order)

            send_success.append(('customer', send_mail(subject=subject,
                                                       message=message,
                                                       from_email=from_email,
                                                       recipient_list=[user.email],
                                                       html_message=html2text.html)))
        return send_success

    def send_fail_email(self):
        logger.debug('Payment Failure')
        send_success = []
        html2text = HTML2TextEmailMessageService(template_name='order/email/payment_admin_fail.html',
                                                 order=self.order)

        # Send Customer Email
        subject = _('TodayCapital.de - Investment Payment, Failure')
        message = html2text.plain_text
        from_email = 'application@todaycapital.de'
        recipient_list = ['post@todaycapital.de']

        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list,
                                                   html_message=html2text.html)))

        return send_success
