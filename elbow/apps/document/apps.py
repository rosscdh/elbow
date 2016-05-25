from __future__ import unicode_literals
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from elbow.utils import get_namedtuple_choices


DOCUMENT_TYPES = get_namedtuple_choices('DOCUMENT_TYPES', (
    ('project', 'project', _('Project Document')),
    ('order', 'order', _('Order Document')),
    ('generic_loan_agreement', 'generic_loan_agreement', _('Generic Loan Agreement')),
    ('loan_agreement', 'loan_agreement', _('Loan Agreement')),
    ('term_sheet', 'term_sheet', _('Term Sheet')),
))

DOCUMENT_STATUS = get_namedtuple_choices('DOCUMENT_STATUS', (
    ('active', 'active', 'Active'),
    ('inactive', 'inactive', 'Inactive'),
))


class DocumentConfig(AppConfig):
    name = 'elbow.apps.document'
