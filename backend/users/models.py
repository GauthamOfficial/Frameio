from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import uuid


class User(AbstractUser):
    """
    Custom user model with Clerk integration and multi-tenant support.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Clerk integration fields
    clerk_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    clerk_created_at = models.DateTimeField(blank=True, null=True)
    clerk_updated_at = models.DateTimeField(blank=True, null=True)
    
    # Profile information
    avatar = models.ImageField(upload_to='users/avatars/', blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Preferences
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    theme = models.CharField(
        max_length=20,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('auto', 'Auto'),
        ],
        default='auto'
    )
    
    # Account status
    is_verified = models.BooleanField(default=False)
    last_active = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def full_name(self):
        """Return the user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username
    
    @property
    def current_organization(self):
        """Get the user's current active organization."""
        active_membership = self.organization_memberships.filter(
            is_active=True
        ).first()
        return active_membership.organization if active_membership else None
    
    def update_last_active(self):
        """Update the user's last active timestamp."""
        self.last_active = timezone.now()
        self.save(update_fields=['last_active'])
    
    def get_organizations(self):
        """Get all organizations the user belongs to."""
        return Organization.objects.filter(
            members__user=self,
            members__is_active=True
        ).distinct()
    
    def can_access_organization(self, organization):
        """Check if user can access a specific organization."""
        return self.organization_memberships.filter(
            organization=organization,
            is_active=True
        ).exists()


class UserSession(models.Model):
    """
    Model for tracking user sessions and activity.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'user_sessions'
        verbose_name = 'User Session'
        verbose_name_plural = 'User Sessions'
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.session_key}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def deactivate(self):
        """Deactivate the session."""
        self.is_active = False
        self.save(update_fields=['is_active'])


class UserActivity(models.Model):
    """
    Model for tracking user activities and actions.
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('design_created', 'Design Created'),
        ('design_updated', 'Design Updated'),
        ('design_deleted', 'Design Deleted'),
        ('ai_generation', 'AI Generation'),
        ('export_design', 'Export Design'),
        ('invite_user', 'Invite User'),
        ('update_profile', 'Update Profile'),
        ('change_password', 'Change Password'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    description = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_activities'
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.action}"


class UserProfile(models.Model):
    """
    Extended user profile model that extends Clerk user with additional fields.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile',
        primary_key=True
    )
    
    # Organization context
    current_organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='current_users'
    )
    
    # Additional profile fields
    job_title = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    company_size = models.CharField(
        max_length=20,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('500+', '500+ employees'),
        ],
        blank=True,
        null=True
    )
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"Profile for {self.user.email}"
    
    def get_current_organization_role(self):
        """Get user's role in current organization."""
        if not self.current_organization:
            return None
        
        try:
            from organizations.models import OrganizationMember
            membership = OrganizationMember.objects.get(
                user=self.user,
                organization=self.current_organization,
                is_active=True
            )
            return membership.role
        except:
            return None


class CompanyProfile(models.Model):
    """
    Company profile model for textile companies to store branding and contact information.
    This model is linked to users and used for brand personalization in AI-generated posters.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='company_profile',
        primary_key=True
    )
    
    # Company branding
    company_name = models.CharField(max_length=255, blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Contact information
    whatsapp_number = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True, help_text="Company contact email address")
    facebook_username = models.CharField(max_length=100, blank=True, null=True, help_text="Facebook username (without @)")
    
    # Additional company details
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Brand preferences for poster generation
    brand_colors = models.JSONField(default=list, blank=True)  # Store brand color palette
    preferred_logo_position = models.CharField(
        max_length=20,
        choices=[
            ('top_right', 'Top Right'),
            ('bottom_right', 'Bottom Right'),
            ('top_left', 'Top Left'),
            ('bottom_left', 'Bottom Left'),
        ],
        default='top_right'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'company_profiles'
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profiles'
    
    def __str__(self):
        return f"Company Profile for {self.user.email}"
    
    @property
    def has_complete_profile(self):
        """Check if the company profile has all essential information."""
        return bool(
            self.company_name and 
            self.whatsapp_number
        )
    
    @property
    def has_logo(self):
        """Check if the company profile has a logo."""
        return bool(self.logo)
    
    def get_contact_info(self):
        """Get formatted contact information."""
        contact_info = {}
        if self.whatsapp_number:
            contact_info['whatsapp'] = self.whatsapp_number
        if self.email:
            contact_info['email'] = self.email
        if self.facebook_username:
            contact_info['facebook'] = self.facebook_username
        return contact_info