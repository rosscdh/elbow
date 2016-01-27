from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    change_form_template = 'order/admin/order_change_form.html'

admin.site.register(Project, ProjectAdmin)
