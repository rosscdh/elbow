# -*- coding: UTF-8 -*-
from django.test import TestCase, Client


VALID_ORDER_POST_DATA = {
    'amount': 2500,
    'has_agreed_to_loan_agreement_terms': True,
    'title': 'Mr',
    'customer_name': 'Bob Dylan Inc.',
    'dob': '1979-03-30',
    'phone': '555-55-55',
    'address_1': '46a BismarkStrasse',
    'address_2': None,
    'postcode': '41069',
    'city': 'Mönchengladbach',
    'country': 'Germany',
    'tax_number': '1234567',
    'payment_type': 'debit',
    't_and_c': True,
    'has_read_contract': True
}


class BaseTestCase(TestCase):
    fixtures = ['project.json']

    def setUp(self):
        self.c = Client()
