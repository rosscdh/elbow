# -*- coding: UTF-8 -*-
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from import_export.admin import ExportMixin
from import_export import resources


class UserResource(resources.ModelResource):

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'userprofile__send_news_and_info', 'last_login', 'date_joined', 'is_active', 'is_superuser', 'is_staff')
        export_order = ('id', 'first_name', 'last_name', 'email', 'userprofile__send_news_and_info', 'last_login', 'date_joined', 'is_active', 'is_superuser', 'is_staff')

    def _is_true(self, value):
        return _('Yes') if value in [1, '1', True, 'True', 'true', 'y', 'yes', 'Yes'] else _('No')

    def dehydrate_userprofile__send_news_and_info(self, obj):
        return self._is_true(obj.userprofile.send_news_and_info)

    def dehydrate_is_active(self, obj):
        return self._is_true(obj.is_active)

    def dehydrate_is_superuser(self, obj):
        return self._is_true(obj.is_superuser)

    def dehydrate_is_staff(self, obj):
        return self._is_true(obj.is_staff)


class UserAdmin(ExportMixin, DjangoUserAdmin):
    resource_class = UserResource
    list_filter = ('userprofile__send_news_and_info', 'is_staff', 'is_superuser', 'is_active', 'groups')


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)