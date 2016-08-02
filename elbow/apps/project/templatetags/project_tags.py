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


@register.inclusion_tag('project/_docs.html', takes_context=True)
def project_docs(context, project):
    is_logged_in = context.get('user').is_authenticated
    specified_docs = list(project.documents.filter(name__icontains='Exposé') | project.documents.filter(name__icontains='Finanzplan'))
    try:
        expose_document = [d for d in specified_docs if u'Expos\xe9' in d.name][0]
    except IndexError:
        expose_document = {'uuid': None}

    try:
        finance_plan = [d for d in specified_docs if u'Finanzplan' in d.name][0]
    except IndexError:
        finance_plan = {'uuid': None}

    return {
        'project_slug': project.slug,
        'expose_document': expose_document,
        'finance_plan': finance_plan,
        'term_sheet': project.term_sheet_doc_permalink,
        'loan_agreement': project.loan_agreement_doc_permalink,
        'documents': project.documents.exclude(pk__in=[d.pk for d in specified_docs]).all(),
        'is_logged_in': is_logged_in
    }
