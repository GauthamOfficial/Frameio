from django.contrib import admin
from .models import PosterGenerationJob, PosterTemplate, PosterGenerationHistory


@admin.register(PosterGenerationJob)
class PosterGenerationJobAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'organization', 'status', 'prompt', 
        'created_at', 'completed_at', 'processing_time', 'cost'
    ]
    list_filter = ['status', 'organization', 'created_at']
    search_fields = ['prompt', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'completed_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'organization', 'status')
        }),
        ('Generation Parameters', {
            'fields': ('prompt', 'negative_prompt', 'design_metadata', 'width', 'height', 'num_images', 'guidance_scale', 'num_inference_steps')
        }),
        ('Results', {
            'fields': ('generated_images', 'thumbnail_url', 'processing_time', 'cost', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        })
    )


@admin.register(PosterTemplate)
class PosterTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'organization', 'usage_count', 
        'is_public', 'is_active', 'created_by', 'created_at'
    ]
    list_filter = ['category', 'is_public', 'is_active', 'organization', 'created_at']
    search_fields = ['name', 'description', 'created_by__email']
    readonly_fields = ['id', 'usage_count', 'created_at', 'updated_at']
    ordering = ['-usage_count', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'description', 'category', 'organization', 'created_by')
        }),
        ('Template Configuration', {
            'fields': ('prompt_template', 'negative_prompt_template', 'default_parameters', 'preview_image')
        }),
        ('Settings', {
            'fields': ('usage_count', 'is_public', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(PosterGenerationHistory)
class PosterGenerationHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'job', 'user_satisfaction_rating', 
        'regeneration_count', 'created_at'
    ]
    list_filter = ['user_satisfaction_rating', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'job__prompt']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'job', 'organization')
        }),
        ('Analytics', {
            'fields': ('user_satisfaction_rating', 'user_feedback', 'regeneration_count', 'final_selection')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )