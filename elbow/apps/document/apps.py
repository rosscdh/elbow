from __future__ import unicode_literals

from django.apps import AppConfig

from elbow.utils import get_namedtuple_choices


DOCUMENT_TYPES = get_namedtuple_choices('DOCUMENT_TYPES', (
    ('project', 'project', 'Project Document'),
    ('order', 'order', 'Order Document'),
    ('large_sum_agreement', 'large_sum_agreement', 'Large Sum Agreement'),
))

DOCUMENT_STATUS = get_namedtuple_choices('DOCUMENT_STATUS', (
    ('active', 'active', 'Active'),
    ('inactive', 'inactive', 'Inactive'),
))


class DocumentConfig(AppConfig):
    name = 'document'
