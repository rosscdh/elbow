# -*- coding: UTF-8 -*-
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from elbow.utils import HTML2TextEmailMessageService


class SendForPaymentService(object):
    """
    Handle the sending of the order for payment processing
    or not
    """
    def __init__(self, order, **kwargs):
        self.order = order

    def should_send_for_payment(self):
        """
        In order to be sent to secupay, we must be in "processing" status AND have a None for transaction_id
        """
        return self.order.can_send_payment

    def send_payment(self):
        return {}

    def send_success_email(self, user_list):
        send_success = []
        html2text = HTML2TextEmailMessageService(template_name='order/email/payment_admin_success.html',
                                                 order=self.order,
                                                 recipients=user_list)
        # Send Admin Email
        subject = _('TodayCapital.de - Investment Payment, Success')
        message = html2text.plain_text
        from_email = 'application@todaycapital.de'
        recipient_list = ['founders@todaycapital.de']

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
        send_success = []
        # Send Customer Email
        subject = _('TodayCapital.de - Investment Payment, Failure')
        message = _('')
        from_email = 'application@todaycapital.de'
        recipient_list = ['founders@todaycapital.de']

        send_success.append(('founders', send_mail(subject=subject,
                                                   message=message,
                                                   from_email=from_email,
                                                   recipient_list=recipient_list)))
        return send_success

    def process(self):
        if self.should_send_for_payment() is True:
            if self.send_payment():
                self.send_success_email()
            else:
                self.send_fail_email()
