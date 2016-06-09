# -*- coding: UTF-8 -*-
from django.test import TestCase, Client


VALID_ORDER_POST_DATA = {
    'amount': 2500,
    'has_agreed_to_loan_agreement_terms': True,
    't_and_c': True,
    'disclosure': True,
    'has_read_investment_contract': True,
    'has_read_loan_agreement_contract': True,
    'title': 'Mr',
    'customer_first_name': 'Bob',
    'customer_last_name': 'Dylan Inc.',
    'company_name': 'BDylan Inc.',
    'dob': '1979-03-30',
    'phone': '555-55-55',
    'address_1': '46a BismarkStrasse',
    'address_2': None,
    'postcode': '41069',
    'city': 'Mönchengladbach',
    'country': 'Germany',
    'tax_number': '1234567',
    'payment_type': 'debit',
}


class BaseTestCase(TestCase):
    fixtures = ['project.json']

    def setUp(self):
        self.c = Client()
