# -*- coding: utf-8 -*-
from django.contrib import admin
from django.conf.urls import url
from django.http import JsonResponse
from django.template.response import TemplateResponse

from pinax.eventlog.models import log

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'proposition', 'amount')
    list_filter = ('status',)
    search_fields = ('slug', 'name', 'order__transaction_id', 'order__user__email')
    change_form_template = 'order/admin/order_change_form.html'

    def get_urls(self):
        urls = super(ProjectAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<pk>\d+)/news/$',
                self.admin_site.admin_view(self.add_news),
                name='add_project_news'),
            url(r'^(?P<project_pk>\d+)/news/(?P<pk>\d+)/$',
                self.admin_site.admin_view(self.delete_news),
                name='project_delete_news'),
        ]
        return my_urls + urls

    def get_project(self, pk):
        return Project.objects.get(pk=pk)

    def delete_news(self, request, project_pk, pk):
        project = self.get_project(pk=pk)
        resp = {}

        if request.method == 'DELETE':
            news_item = project.news_history.get(pk=pk)
            news_item.delete()
            resp.update({'message': 'Deleted News Item'})

        return JsonResponse(resp)

    def add_news(self, request, pk):
        project = self.get_project(pk=pk)
        resp = {}

        if request.method == 'POST':
            log(
                user=request.user,
                action="project.news",
                obj=project,
                extra={
                    "note": request.POST.get('note')
                }
            )
            return JsonResponse(resp)
        else:
            resp = {
                'is_popup': True,
                'project': project,
                'object_list': project.news_history,
            }
            return TemplateResponse(request,
                                    'project/admin/project-news.html',
                                    resp)

admin.site.register(Project, ProjectAdmin)
