from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid


class Organization(models.Model):
    """
    Multi-tenant organization model for isolating data between different organizations.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='organizations/logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    
    # Subscription and billing
    subscription_plan = models.CharField(
        max_length=50,
        choices=[
            ('free', 'Free'),
            ('basic', 'Basic'),
            ('premium', 'Premium'),
            ('enterprise', 'Enterprise'),
        ],
        default='free'
    )
    subscription_status = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('suspended', 'Suspended'),
            ('cancelled', 'Cancelled'),
        ],
        default='active'
    )
    
    # Usage tracking
    ai_generations_used = models.PositiveIntegerField(default=0)
    ai_generations_limit = models.PositiveIntegerField(default=10)  # Free plan limit
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.subscription_status == 'active'
    
    @property
    def can_generate_ai(self):
        return self.is_active and self.ai_generations_used < self.ai_generations_limit
    
    def increment_ai_usage(self):
        """Increment AI generation usage counter."""
        self.ai_generations_used += 1
        self.save(update_fields=['ai_generations_used'])


class OrganizationMember(models.Model):
    """
    Model for managing organization membership and roles.
    """
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('designer', 'Designer'),
        ('viewer', 'Viewer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='members'
    )
    user = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='organization_memberships'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='designer')
    is_active = models.BooleanField(default=True)
    
    # Permissions
    can_invite_users = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organization_members'
        unique_together = ['organization', 'user']
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"
    
    @property
    def is_owner(self):
        return self.role == 'owner'
    
    @property
    def is_admin(self):
        return self.role in ['owner', 'admin']
    
    @property
    def can_manage_users(self):
        return self.role in ['owner', 'admin', 'manager']


class OrganizationInvitation(models.Model):
    """
    Model for managing organization invitations.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='invitations'
    )
    email = models.EmailField()
    role = models.CharField(max_length=20, choices=OrganizationMember.ROLE_CHOICES)
    invited_by = models.ForeignKey(
        'users.User', 
        on_delete=models.CASCADE, 
        related_name='sent_invitations'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    token = models.CharField(max_length=255, unique=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    responded_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'organization_invitations'
        unique_together = ['organization', 'email']
        verbose_name = 'Organization Invitation'
        verbose_name_plural = 'Organization Invitations'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Invitation to {self.email} for {self.organization.name}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def accept(self, user):
        """Accept the invitation and create organization membership."""
        if self.is_expired or self.status != 'pending':
            return False
        
        # Create organization membership
        OrganizationMember.objects.create(
            organization=self.organization,
            user=user,
            role=self.role
        )
        
        # Update invitation status
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        return True
    
    def decline(self):
        """Decline the invitation."""
        if self.status != 'pending':
            return False
        
        self.status = 'declined'
        self.responded_at = timezone.now()
        self.save()
        
        return True