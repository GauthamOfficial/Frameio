from django.db import models
from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.mixins import TenantScopedModel, TenantScopedManager
import uuid
from django.utils import timezone

User = get_user_model()


class DesignShare(TenantScopedModel):
    """Model to track design sharing"""
    
    ACCESS_LEVEL_CHOICES = [
        ('view', 'View Only'),
        ('comment', 'Comment'),
        ('edit', 'Edit'),
        ('admin', 'Admin'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('revoked', 'Revoked'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey('designs.Design', on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_designs')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_shares', null=True, blank=True)
    access_level = models.CharField(max_length=20, choices=ACCESS_LEVEL_CHOICES, default='view')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Sharing options
    share_token = models.CharField(max_length=100, unique=True, blank=True)  # For public sharing
    is_public = models.BooleanField(default=False)
    allow_download = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Expiration
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    message = models.TextField(blank=True)  # Optional message when sharing
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_shares'
        verbose_name = 'Design Share'
        verbose_name_plural = 'Design Shares'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'design']),
            models.Index(fields=['shared_by']),
            models.Index(fields=['shared_with']),
            models.Index(fields=['share_token']),
            models.Index(fields=['status', 'expires_at']),
        ]
        unique_together = ['design', 'shared_with', 'organization']  # One share per user per design
    
    def __str__(self):
        if self.shared_with:
            return f"{self.design.title} shared with {self.shared_with.get_full_name()}"
        else:
            return f"{self.design.title} shared publicly"
    
    def is_expired(self):
        """Check if share has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at
    
    def revoke(self):
        """Revoke the share"""
        self.status = 'revoked'
        self.save(update_fields=['status', 'updated_at'])
    
    def can_access(self, user):
        """Check if user can access this shared design"""
        if self.status != 'active':
            return False
        
        if self.is_expired():
            self.status = 'expired'
            self.save(update_fields=['status'])
            return False
        
        # Owner can always access
        if self.design.created_by == user:
            return True
        
        # Check if user is the one shared with
        if self.shared_with and self.shared_with == user:
            return True
        
        # Check if user is in the same organization and has appropriate permissions
        if user.current_organization == self.organization:
            from organizations.models import OrganizationMember
            try:
                membership = OrganizationMember.objects.get(
                    user=user,
                    organization=self.organization,
                    is_active=True
                )
                # Admin and Manager can access all shared designs
                if membership.role in ['admin', 'manager']:
                    return True
            except OrganizationMember.DoesNotExist:
                pass
        
        return False


class DesignComment(TenantScopedModel):
    """Model for design comments"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey('designs.Design', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    is_resolved = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_comments'
        verbose_name = 'Design Comment'
        verbose_name_plural = 'Design Comments'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['organization', 'design']),
            models.Index(fields=['author']),
            models.Index(fields=['parent_comment']),
        ]
    
    def __str__(self):
        return f"Comment by {self.author.get_full_name()} on {self.design.title}"
    
    def can_edit(self, user):
        """Check if user can edit this comment"""
        return self.author == user or user.is_staff
    
    def can_delete(self, user):
        """Check if user can delete this comment"""
        return self.author == user or user.is_staff


class DesignCollaboration(TenantScopedModel):
    """Model to track design collaboration sessions"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey('designs.Design', on_delete=models.CASCADE, related_name='collaborations')
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_collaborations')
    participants = models.ManyToManyField(User, related_name='collaborations', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Collaboration settings
    allow_edit = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=True)
    auto_save = models.BooleanField(default=True)
    
    # Session data
    session_data = models.JSONField(default=dict, blank=True)  # Store collaboration session data
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_collaborations'
        verbose_name = 'Design Collaboration'
        verbose_name_plural = 'Design Collaborations'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['organization', 'design']),
            models.Index(fields=['initiator']),
            models.Index(fields=['status']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Collaboration on {self.design.title} by {self.initiator.get_full_name()}"
    
    def add_participant(self, user):
        """Add a participant to the collaboration"""
        if user not in self.participants.all():
            self.participants.add(user)
            self.last_activity = timezone.now()
            self.save(update_fields=['last_activity'])
    
    def remove_participant(self, user):
        """Remove a participant from the collaboration"""
        if user in self.participants.all():
            self.participants.remove(user)
            self.last_activity = timezone.now()
            self.save(update_fields=['last_activity'])
    
    def can_join(self, user):
        """Check if user can join this collaboration"""
        # Owner can always join
        if self.design.created_by == user:
            return True
        
        # Initiator can always join
        if self.initiator == user:
            return True
        
        # Check if user has access to the design
        shares = DesignShare.objects.filter(
            design=self.design,
            shared_with=user,
            status='active',
            organization=self.organization
        )
        
        if shares.exists():
            share = shares.first()
            return share.access_level in ['edit', 'admin']
        
        return False
    
    def end_collaboration(self):
        """End the collaboration session"""
        self.status = 'completed'
        self.ended_at = timezone.now()
        self.save(update_fields=['status', 'ended_at'])


class DesignVersion(TenantScopedModel):
    """Model to track design versions for collaboration"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey('designs.Design', on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_versions')
    collaboration = models.ForeignKey(DesignCollaboration, on_delete=models.CASCADE, null=True, blank=True, related_name='versions')
    
    # Version data
    version_data = models.JSONField(default=dict, blank=True)  # Store version-specific data
    changes_summary = models.TextField(blank=True)  # Summary of changes made
    
    # File data
    image = models.ImageField(upload_to='designs/versions/', blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_versions'
        verbose_name = 'Design Version'
        verbose_name_plural = 'Design Versions'
        ordering = ['-version_number']
        indexes = [
            models.Index(fields=['organization', 'design']),
            models.Index(fields=['created_by']),
            models.Index(fields=['collaboration']),
        ]
        unique_together = ['design', 'version_number', 'organization']
    
    def __str__(self):
        return f"Version {self.version_number} of {self.design.title}"
    
    def restore(self):
        """Restore this version as the current design"""
        # Update the main design with this version's data
        self.design.image = self.image
        self.design.metadata = self.version_data
        self.design.updated_at = timezone.now()
        self.design.save(update_fields=['image', 'metadata', 'updated_at'])


class DesignActivity(TenantScopedModel):
    """Model to track design activity for collaboration"""
    
    ACTIVITY_TYPES = [
        ('view', 'View'),
        ('edit', 'Edit'),
        ('comment', 'Comment'),
        ('share', 'Share'),
        ('export', 'Export'),
        ('version', 'Version Created'),
        ('collaboration_start', 'Collaboration Started'),
        ('collaboration_end', 'Collaboration Ended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    design = models.ForeignKey('designs.Design', on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='design_activities')
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    
    # Activity data
    activity_data = models.JSONField(default=dict, blank=True)  # Store activity-specific data
    description = models.TextField(blank=True)  # Human-readable description
    
    # Related objects
    related_comment = models.ForeignKey(DesignComment, on_delete=models.CASCADE, null=True, blank=True)
    related_collaboration = models.ForeignKey(DesignCollaboration, on_delete=models.CASCADE, null=True, blank=True)
    related_version = models.ForeignKey(DesignVersion, on_delete=models.CASCADE, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'design_activities'
        verbose_name = 'Design Activity'
        verbose_name_plural = 'Design Activities'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'design']),
            models.Index(fields=['user']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} {self.get_activity_type_display()} {self.design.title}"