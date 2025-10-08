from django.db import models
from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.mixins import TenantScopedModel, TenantScopedManager
import uuid
from django.utils import timezone

User = get_user_model()


class ExportJob(TenantScopedModel):
    """Model to track design export jobs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    EXPORT_FORMAT_CHOICES = [
        ('png', 'PNG'),
        ('jpg', 'JPG'),
        ('pdf', 'PDF'),
        ('svg', 'SVG'),
        ('zip', 'ZIP'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Export parameters
    design_ids = models.JSONField(default=list)  # List of design IDs to export
    export_format = models.CharField(max_length=10, choices=EXPORT_FORMAT_CHOICES)
    export_options = models.JSONField(default=dict, blank=True)  # Additional export options
    
    # Results
    export_file_path = models.CharField(max_length=500, blank=True, null=True)
    download_url = models.URLField(blank=True, null=True)
    file_size = models.BigIntegerField(null=True, blank=True)  # File size in bytes
    processing_time = models.FloatField(null=True, blank=True)  # Time in seconds
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # When download link expires
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'export_jobs'
        verbose_name = 'Export Job'
        verbose_name_plural = 'Export Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Export Job {self.id} - {self.export_format} - {self.status}"
    
    def mark_processing(self):
        """Mark job as processing"""
        self.status = 'processing'
        self.save(update_fields=['status'])
    
    def mark_completed(self, export_file_path=None, download_url=None, file_size=None, processing_time=None):
        """Mark job as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.expires_at = timezone.now() + timezone.timedelta(hours=24)  # Expire in 24 hours
        
        if export_file_path:
            self.export_file_path = export_file_path
        if download_url:
            self.download_url = download_url
        if file_size:
            self.file_size = file_size
        if processing_time:
            self.processing_time = processing_time
            
        self.save(update_fields=[
            'status', 'completed_at', 'expires_at', 'export_file_path',
            'download_url', 'file_size', 'processing_time'
        ])
    
    def mark_failed(self, error_message):
        """Mark job as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])
    
    def cancel(self):
        """Cancel the job"""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def is_expired(self):
        """Check if download link has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class ExportTemplate(TenantScopedModel):
    """Model to store export templates"""
    
    TEMPLATE_TYPE_CHOICES = [
        ('single', 'Single Design'),
        ('batch', 'Batch Export'),
        ('catalog', 'Catalog Export'),
        ('custom', 'Custom Layout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPE_CHOICES)
    
    # Template configuration
    export_format = models.CharField(max_length=10, choices=ExportJob.EXPORT_FORMAT_CHOICES)
    export_options = models.JSONField(default=dict, blank=True)
    layout_config = models.JSONField(default=dict, blank=True)  # Layout configuration
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_export_templates')
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'export_templates'
        verbose_name = 'Export Template'
        verbose_name_plural = 'Export Templates'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['organization', 'template_type']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class ExportHistory(TenantScopedModel):
    """Model to store export history for analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_history')
    export_job = models.OneToOneField(ExportJob, on_delete=models.CASCADE, related_name='history')
    
    # Analytics data
    download_count = models.IntegerField(default=0)
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'export_history'
        verbose_name = 'Export History'
        verbose_name_plural = 'Export Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export History for {self.export_job}"
    
    def increment_download_count(self):
        """Increment download count"""
        self.download_count += 1
        self.save(update_fields=['download_count'])