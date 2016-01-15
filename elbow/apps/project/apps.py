# -*- coding: UTF-8 -*-
from django.apps import AppConfig

from elbow.utils import get_namedtuple_choices


PROJECT_STATUS = get_namedtuple_choices('PROJECT_STATUS', (
    ('pending', 'pending', 'Pending'),
    ('active', 'active', 'Available'),
    ('complete', 'complete', 'Complete'),
))

USE_PAYMENTOPTIONS = get_namedtuple_choices('USE_PAYMENTOPTIONS', (
    ('yes', 'yes', 'Yes'),
    ('no', 'no', 'No'),
))


class ProjectConfig(AppConfig):
    name = 'project'
