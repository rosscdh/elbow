from django.contrib import admin

from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'document_type', 'created_at', 'status')
    list_filter = ('document_type', 'status',)
    search_fields = ('uuid', 'name', 'document_type', 'status')


admin.site.register(Document, DocumentAdmin)
