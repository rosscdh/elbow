from django.contrib import admin

from .models import Document


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'document_type', 'created_at', 'status')
    list_filter = ('document_type', 'status',)
    search_fields = ('uuid', 'name', 'document_type', 'status')


class ProjectDocument(Document):
    class Meta:
        proxy = True


class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'created_at', 'status')
    list_filter = ('document_type', 'status',)
    search_fields = ('uuid', 'name', 'status')

    def get_queryset(self, request):
        return super(ProjectDocumentAdmin, self).get_queryset(request).filter(document_type__in=['project',
                                                                                                 'generic_loan_agreement',
                                                                                                 'loan_agreement',
                                                                                                 'term_sheet',])


class OrderDocument(Document):
    class Meta:
        proxy = True


class OrderDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'uuid', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('uuid', 'name', 'status')

    def get_queryset(self, request):
        return super(OrderDocumentAdmin, self).get_queryset(request).filter(document_type__in=['order', 'loan_agreement'])


admin.site.register(Document, DocumentAdmin)
admin.site.register(ProjectDocument, ProjectDocumentAdmin)
admin.site.register(OrderDocument, OrderDocumentAdmin)
