# admin.py
from django.contrib import admin
from .models import RetrievalDocument

@admin.register(RetrievalDocument)
class RetrievalDocumentAdmin(admin.ModelAdmin):
    list_display = ('response_mode', 'source_document_name', 'vectorstore_name', 'created_at', 'updated_at')
    search_fields = ('response_mode', 'source_document_name')