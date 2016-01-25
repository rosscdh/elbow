# -*- coding: UTF-8 -*-

from .services import SendForPaymentService


def post_save_send_payment_request(sender, instance, **kwargs):
    """
    Main signal to send the secupay payment signal
    should the Order bet set to status "processing"
    should the Order have no "transaction_id" (has not yet been sent)
    """
    if instance.status in [instance.__class__.ORDER_STATUS.processing]  \
       and instance.token in [None, '']:
            #  Send payment request
            service = SendForPaymentService(order=instance)
            service.process()
