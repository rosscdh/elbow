# -*- coding: UTF-8 -*-

from .services import SendForPaymentService


def post_save_send_payment_request(sender, instance, **kwargs):
    """
    Main signal to send the secupay payment signal
    should the Order bet set to status "processing"
    should the Order have no "transaction_id" (has not yet been sent)
    """
    if instance.can_send_payment is True:
        #  Send payment request
        service = SendForPaymentService(order=instance)
        service.process()
