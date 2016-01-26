from django.contrib import admin

from elbow.apps.order.models import Order
from elbow.apps.order.forms import OrderAdminLimitedListForm
from .models import Project


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    can_delete = False
    form = OrderAdminLimitedListForm


class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        OrderInline
    ]

admin.site.register(Project, ProjectAdmin)
