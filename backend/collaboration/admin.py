from django.contrib import admin
from .models import (
    DesignShare, DesignComment, DesignCollaboration, 
    DesignVersion, DesignActivity
)


@admin.register(DesignShare)
class DesignShareAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'design', 'shared_by', 'shared_with', 'access_level', 
        'status', 'is_public', 'created_at', 'expires_at'
    ]
    list_filter = ['access_level', 'status', 'is_public', 'organization', 'created_at']
    search_fields = [
        'design__title', 'shared_by__email', 'shared_with__email', 
        'shared_by__first_name', 'shared_with__first_name'
    ]
    readonly_fields = ['id', 'share_token', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'design', 'shared_by', 'shared_with', 'organization')
        }),
        ('Access Control', {
            'fields': ('access_level', 'status', 'is_public', 'allow_download', 'allow_comments')
        }),
        ('Sharing Details', {
            'fields': ('share_token', 'message', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DesignComment)
class DesignCommentAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'design', 'author', 'parent_comment', 'is_resolved', 'created_at'
    ]
    list_filter = ['is_resolved', 'organization', 'created_at']
    search_fields = [
        'design__title', 'author__email', 'author__first_name', 
        'author__last_name', 'content'
    ]
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'design', 'author', 'parent_comment', 'organization')
        }),
        ('Comment Content', {
            'fields': ('content', 'is_resolved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        })
    )


@admin.register(DesignCollaboration)
class DesignCollaborationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'design', 'initiator', 'status', 'participants_count', 
        'started_at', 'last_activity', 'ended_at'
    ]
    list_filter = ['status', 'organization', 'started_at', 'last_activity']
    search_fields = [
        'design__title', 'initiator__email', 'initiator__first_name', 
        'initiator__last_name'
    ]
    readonly_fields = ['id', 'started_at', 'last_activity', 'ended_at']
    ordering = ['-last_activity']
    filter_horizontal = ['participants']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'design', 'initiator', 'organization', 'status')
        }),
        ('Collaboration Settings', {
            'fields': ('allow_edit', 'allow_comments', 'auto_save')
        }),
        ('Participants', {
            'fields': ('participants',)
        }),
        ('Session Data', {
            'fields': ('session_data',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'last_activity', 'ended_at')
        })
    )
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participants'


@admin.register(DesignVersion)
class DesignVersionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'design', 'version_number', 'created_by', 
        'collaboration', 'created_at'
    ]
    list_filter = ['version_number', 'organization', 'created_at']
    search_fields = [
        'design__title', 'created_by__email', 'created_by__first_name', 
        'created_by__last_name', 'changes_summary'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-version_number']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'design', 'version_number', 'created_by', 'organization')
        }),
        ('Version Details', {
            'fields': ('collaboration', 'version_data', 'changes_summary', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )


@admin.register(DesignActivity)
class DesignActivityAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'design', 'user', 'activity_type', 'created_at'
    ]
    list_filter = ['activity_type', 'organization', 'created_at']
    search_fields = [
        'design__title', 'user__email', 'user__first_name', 
        'user__last_name', 'description'
    ]
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'design', 'user', 'organization', 'activity_type')
        }),
        ('Activity Details', {
            'fields': ('activity_data', 'description')
        }),
        ('Related Objects', {
            'fields': ('related_comment', 'related_collaboration', 'related_version')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        })
    )