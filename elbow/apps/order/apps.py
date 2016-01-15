# -*- coding: UTF-8 -*-
from django.apps import AppConfig
from elbow.utils import get_namedtuple_choices


ORDER_STATUS = get_namedtuple_choices('ORDER_STATUS', (
    ('pending', 'pending', 'Pending'),
))


class OrderConfig(AppConfig):
    name = 'order'
