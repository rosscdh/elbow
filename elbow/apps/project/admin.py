from django.contrib import admin

from .models import Project


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('slug', 'name', 'proposition', 'amount')
    list_filter = ('status',)
    search_fields = ('slug', 'name', 'order__transaction_id', 'order__user__email')

    change_form_template = 'order/admin/order_change_form.html'

admin.site.register(Project, ProjectAdmin)
