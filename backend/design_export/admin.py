from django.contrib import admin
from .models import ExportJob, ExportTemplate, ExportHistory


@admin.register(ExportJob)
class ExportJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'organization', 'status', 'export_format', 
        'created_at', 'completed_at', 'file_size', 'processing_time'
    ]
    list_filter = ['status', 'export_format', 'organization', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at', 'expires_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'organization', 'status')
        }),
        ('Export Parameters', {
            'fields': ('design_ids', 'export_format', 'export_options')
        }),
        ('Results', {
            'fields': ('export_file_path', 'download_url', 'file_size', 'processing_time', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at', 'expires_at')
        })
    )


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template_type', 'export_format', 'organization', 
        'usage_count', 'is_public', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['template_type', 'export_format', 'is_public', 'is_active', 'organization', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']
    ordering = ['-usage_count', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'template_type', 'organization', 'created_by')
        }),
        ('Template Configuration', {
            'fields': ('export_format', 'export_options', 'layout_config')
        }),
        ('Settings', {
            'fields': ('usage_count', 'is_public', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(ExportHistory)
class ExportHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'export_job', 'download_count', 'created_at'
    ]
    list_filter = ['download_count', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'export_job', 'organization')
        }),
        ('Analytics', {
            'fields': ('download_count', 'user_feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )