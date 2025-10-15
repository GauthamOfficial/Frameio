from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import User, UserProfile, UserActivity, CompanyProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom admin interface for User model with enhanced display and filtering.
    """
    list_display = [
        'email', 'username', 'first_name', 'last_name', 'is_verified', 
        'is_active', 'is_staff', 'created_at', 'last_active', 'clerk_id'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_verified', 
        'created_at', 'last_active', 'theme', 'language'
    ]
    search_fields = ['email', 'username', 'first_name', 'last_name', 'clerk_id']
    ordering = ['-created_at']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'username', 'email', 'first_name', 'last_name')
        }),
        ('Clerk Integration', {
            'fields': ('clerk_id', 'clerk_created_at', 'clerk_updated_at'),
            'classes': ('collapse',)
        }),
        ('Profile Information', {
            'fields': ('avatar', 'phone_number', 'bio', 'location', 'website'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('timezone', 'language', 'theme'),
            'classes': ('collapse',)
        }),
        ('Account Status', {
            'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser', 'last_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Basic Information', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'password1', 'password2'),
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related for better performance."""
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for UserProfile model.
    """
    list_display = [
        'user_email', 'user_username', 'job_title', 'department', 
        'company_size', 'current_organization', 'created_at'
    ]
    list_filter = [
        'company_size', 'email_notifications', 'push_notifications', 
        'marketing_emails', 'created_at', 'current_organization'
    ]
    search_fields = [
        'user__email', 'user__username', 'user__first_name', 
        'user__last_name', 'job_title', 'department'
    ]
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['user', 'current_organization']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'current_organization')
        }),
        ('Professional Information', {
            'fields': ('job_title', 'department', 'company_size')
        }),
        ('Notification Preferences', {
            'fields': ('email_notifications', 'push_notifications', 'marketing_emails')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'Email'
    user_email.admin_order_field = 'user__email'
    
    def user_username(self, obj):
        """Display user username."""
        return obj.user.username
    user_username.short_description = 'Username'
    user_username.admin_order_field = 'user__username'


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """
    Admin interface for UserActivity model to track user actions.
    """
    list_display = [
        'user_email', 'action', 'ip_address', 'description_short', 
        'created_at'
    ]
    list_filter = [
        'action', 'created_at', 'ip_address'
    ]
    search_fields = [
        'user__email', 'user__username', 'action', 'ip_address', 'description'
    ]
    readonly_fields = ['created_at']
    raw_id_fields = ['user']
    date_hierarchy = 'created_at'
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def description_short(self, obj):
        """Display shortened description."""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('user')


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    """
    Admin interface for CompanyProfile model.
    """
    list_display = [
        'user_email', 'company_name', 'website', 'whatsapp_number', 
        'created_at', 'has_complete_profile'
    ]
    list_filter = [
        'preferred_logo_position', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__username', 'company_name', 'website', 'description'
    ]
    readonly_fields = ['created_at', 'updated_at', 'has_complete_profile']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'logo', 'website', 'address', 'description')
        }),
        ('Contact Information', {
            'fields': ('whatsapp_number', 'email', 'facebook_link')
        }),
        ('Brand Preferences', {
            'fields': ('brand_colors', 'preferred_logo_position'),
            'classes': ('collapse',)
        }),
        ('Profile Status', {
            'fields': ('has_complete_profile',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_email(self, obj):
        """Display user email."""
        return obj.user.email
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'
    
    def has_complete_profile(self, obj):
        """Display if profile is complete."""
        return obj.has_complete_profile
    has_complete_profile.boolean = True
    has_complete_profile.short_description = 'Complete Profile'


# Customize admin site header and title
admin.site.site_header = "Frameio Admin"
admin.site.site_title = "Frameio Admin Portal"
admin.site.index_title = "Welcome to Frameio Administration"
