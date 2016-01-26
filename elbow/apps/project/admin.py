from django.contrib import admin

from elbow.apps.order.models import Order
from elbow.apps.order.forms import OrderAdminLimitedListForm
from .models import Project


class OrderInline(admin.TabularInline):
    model = Order
    extra = 0
    can_delete = False
    form = OrderAdminLimitedListForm
    template = 'order/admin/limited_list_inline.html'

    def get_queryset(self, request):
        qs = super(OrderInline, self).get_queryset(request)
        return qs.order_by('-created_at', '-updated_at', '-pk')


class ProjectAdmin(admin.ModelAdmin):
    inlines = [
        OrderInline
    ]

admin.site.register(Project, ProjectAdmin)
