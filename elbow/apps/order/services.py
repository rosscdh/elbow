# -*- coding: UTF-8 -*-
from elbow.apps.public.services import SendEmailService

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
