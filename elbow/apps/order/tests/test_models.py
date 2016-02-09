# -*- coding: UTF-8 -*-
from django.core import mail
from django.contrib.contenttypes.models import ContentType

import json
import httpretty
from model_mommy import mommy

from . import BaseTestCase


class OrderModelTest(BaseTestCase):
    """
    UnitTest the service methods, with a VALID order object
    """

    def setUp(self):
        super(OrderModelTest, self).setUp()
        mail.outbox = []
        self.order = mommy.make('order.Order',
                                   status='processing',  # Must be in processing
                                   transaction_id=None,
                                   amount=250.25)  # AND must NOT have a transaction_id
        self.order.user.email = 'bob@example.com'  # Set the email of the order User

    def test_can_send_payment(self):
        self.assertTrue(self.order.can_send_payment)

    def test_content_type(self):
        self.assertEqual(self.order.content_type, ContentType.objects.filter(app_label='order', model='order').first())

    def test_log_history(self):
        self.assertEqual(self.order.log_history.__class__.__name__, 'QuerySet')

    def test_url_success(self):
        self.assertEqual(self.order.url_success, u'/de/orders/%s/order/%s/payment/successful/' % (self.order.project.slug, self.order.uuid))

    def test_url_failure(self):
        self.assertEqual(self.order.url_failure, u'/de/orders/%s/order/%s/payment/failure/' % (self.order.project.slug, self.order.uuid))

    def test_url_webhooks(self):
        self.assertEqual(self.order.url_webhook, u'/de/orders/%s/order/%s/payment/webhook/' % (self.order.project.slug, self.order.uuid))

    def test_url(self):
        self.order.status = self.order.ORDER_STATUS.paid
        self.assertEqual(self.order.url, u'/de/orders/%s/order/%s/' % (self.order.project.slug, self.order.uuid))

        self.order.status = self.order.ORDER_STATUS.processing
        self.assertEqual(self.order.url, u'/de/orders/%s/order/%s/' % (self.order.project.slug, self.order.uuid))

        # If we have a large amount to pay then take us to the large-sum-agreement page
        self.order.status = self.order.ORDER_STATUS.more_info
        self.order.amount = 250000.00
        self.assertEqual(self.order.url, u'/de/orders/%s/order/%s/large-sum-agreement/' % (self.order.project.slug, self.order.uuid))

        # If we have only a small amount to pay then take us direct to payment
        self.order.status = self.order.ORDER_STATUS.more_info
        self.order.amount = 250.00
        self.assertEqual(self.order.url, u'/de/orders/%s/order/%s/payment/' % (self.order.project.slug, self.order.uuid))

        self.order.status = self.order.ORDER_STATUS.large_sum_agreement
        self.assertEqual(self.order.url, u'/de/orders/%s/order/%s/payment/' % (self.order.project.slug, self.order.uuid))



    @httpretty.activate
    def test_valid_make_payment(self):
        expected_response = {
            "status": "ok",
            "data": {
                "hash": "tujevzgobryk3303",
                "iframe_url": "https://api.secupay.ag/payment/tujevzgobryk3303"
            },
            "errors": None
        }
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/init",
                               body=json.dumps(expected_response),
                               content_type="application/json")

        with self.settings(DEBUG=True):
            resp = self.order.make_payment(user=self.order.user)

        self.assertTrue(type(resp) is tuple)
        self.assertTrue(len(resp) is 2)
        self.assertTrue(resp[0].__class__.__name__ == 'Order')
        self.assertTrue(type(resp[1]) is dict)

        self.assertEqual(self.order.transaction_id, 'tujevzgobryk3303')
        self.assertEqual(self.order.data, {u'iframe_url': u'https://api.secupay.ag/payment/tujevzgobryk3303', u'hash': u'tujevzgobryk3303'})

    @httpretty.activate
    def test_prepay_payment_type(self):
        expected_response = {
          "status": "ok",
          "errors": None,
          "data": {
            "iframe_url": "https://api-dist.secupay-ag.de/payment/yvxsekbprziw962155",
            "hash": "yvxsekbprziw962155",
            "purpose": "TA 6082993",
            "payment_data": {
              "bankcode": "30050000",
              "accountowner": "secupay AG",
              "iban": "DE88300500000001747013",
              "bic": "WELADEDDXXX",
              "accountnumber": "1747013"
            }
          }
        }
        httpretty.register_uri(httpretty.POST, "https://api-dist.secupay-ag.de/payment/init",
                               body=json.dumps(expected_response),
                               content_type="application/json")
        self.order.payment_type = self.order.ORDER_PAYMENT_TYPE.prepay
        self.order.save(update_fields=['payment_type'])

        with self.settings(DEBUG=True):
            resp = self.order.make_payment(user=self.order.user)

        self.assertTrue(type(resp) is tuple)
        self.assertTrue(len(resp) is 2)
        self.assertTrue(resp[0].__class__.__name__ == 'Order')
        self.assertTrue(type(resp[1]) is dict)

        self.assertEqual(self.order.transaction_id, 'yvxsekbprziw962155')
        self.assertEqual(self.order.data, {"hash": "yvxsekbprziw962155",
                                           "iframe_url": "https://api-dist.secupay-ag.de/payment/yvxsekbprziw962155",
                                           "payment_data": {
                                             "accountnumber": "1747013",
                                             "accountowner": "secupay AG",
                                             "bankcode": "30050000",
                                             "bic": "WELADEDDXXX",
                                             "iban": "DE88300500000001747013"
                                           },
                                           "purpose": "TA 6082993"
                                          })

