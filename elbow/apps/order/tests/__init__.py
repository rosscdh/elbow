# -*- coding: UTF-8 -*-
from django.test import TestCase, Client


VALID_ORDER_POST_DATA = {
    'amount': 250,
    'customer_name': 'Bob Dylan Inc.',
    'phone': '555-55-55',
    'address': '46a BismarkStrasse Mönchengladbach, NRW',
    'country': 'Germany',
    'payment_type': 'debit',
    't_and_c': True,
    'has_read_contract': True
}


class BaseTestCase(TestCase):
    fixtures = ['project.json']

    def setUp(self):
        self.c = Client()
