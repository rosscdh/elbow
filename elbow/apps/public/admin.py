from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin


class UserAdmin(DjangoUserAdmin):
    list_filter = ('userprofile__send_news_and_info', 'is_staff', 'is_superuser', 'is_active', 'groups')


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)