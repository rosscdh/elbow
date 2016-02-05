# -*- coding: UTF-8 -*-
from django import template
from elbow.apps.project.models import Project

register = template.Library()


@register.inclusion_tag('order/_user_orders_for_project.html')
def project_user_orders(project, user):
    queryset = project.order_set.filter(user=user)
    return {
        'user': user,
        'order_list': queryset,
    }
