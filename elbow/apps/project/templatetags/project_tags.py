# -*- coding: UTF-8 -*-
from django import template
from elbow.apps.project.models import Project

register = template.Library()


@register.inclusion_tag('project/_preview.html')
def project_preview(queryset=None):
    queryset = Project.objects.public() if queryset in [None, ''] else queryset
    return {
        'project_list': queryset,
    }


@register.inclusion_tag('project/_stats.html')
def project_stats(project):
    return {
        'project': project,
    }
