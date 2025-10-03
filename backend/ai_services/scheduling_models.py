from django.db import models
from django.contrib.auth import get_user_model
from organizations.models import Organization
import uuid
from django.utils import timezone

User = get_user_model()


class ScheduledPost(models.Model):
    """Model for scheduling social media posts"""
    
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('whatsapp', 'WhatsApp'),
        ('twitter', 'Twitter'),
        ('linkedin', 'LinkedIn'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('scheduled', 'Scheduled'),
        ('posted', 'Posted'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='scheduled_posts')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scheduled_posts')
    
    # Post details
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    asset_url = models.URLField(help_text="URL of the image/video asset to post")
    caption = models.TextField(help_text="Post caption with hashtags")
    
    # Scheduling
    scheduled_time = models.DateTimeField(help_text="When the post should be published")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True, help_text="When the post was actually published")
    
    # Error handling
    error_message = models.TextField(blank=True, null=True, help_text="Error message if posting failed")
    retry_count = models.IntegerField(default=0, help_text="Number of retry attempts")
    max_retries = models.IntegerField(default=3, help_text="Maximum number of retry attempts")
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional post metadata")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['scheduled_time']),
            models.Index(fields=['platform', 'status']),
        ]
    
    def __str__(self):
        return f"{self.platform} post - {self.status} ({self.organization.name})"
    
    def is_ready_to_post(self):
        """Check if the post is ready to be published"""
        return (
            self.status == 'scheduled' and 
            timezone.now() >= self.scheduled_time
        )
    
    def mark_as_posted(self, posted_at=None):
        """Mark the post as successfully posted"""
        self.status = 'posted'
        self.posted_at = posted_at or timezone.now()
        self.save(update_fields=['status', 'posted_at'])
    
    def mark_as_failed(self, error_message):
        """Mark the post as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.retry_count += 1
        self.save(update_fields=['status', 'error_message', 'retry_count'])
    
    def can_retry(self):
        """Check if the post can be retried"""
        return self.retry_count < self.max_retries
    
    def schedule_for_retry(self):
        """Schedule the post for retry"""
        if self.can_retry():
            self.status = 'pending'
            self.save(update_fields=['status'])
            return True
        return False
