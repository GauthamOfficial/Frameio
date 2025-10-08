from django.db import models
from django.contrib.auth import get_user_model
from organizations.models import Organization
from organizations.mixins import TenantScopedModel, TenantScopedManager
import uuid
from django.utils import timezone

User = get_user_model()


class PosterGenerationJob(TenantScopedModel):
    """Model to track AI poster generation jobs"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poster_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Generation parameters
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, null=True)
    design_metadata = models.JSONField(default=dict, blank=True)
    
    # Generation settings
    width = models.IntegerField(default=1024)
    height = models.IntegerField(default=1024)
    num_images = models.IntegerField(default=1)
    guidance_scale = models.FloatField(default=7.5)
    num_inference_steps = models.IntegerField(default=20)
    
    # Results
    generated_images = models.JSONField(default=list, blank=True)  # List of image URLs
    thumbnail_url = models.URLField(blank=True, null=True)
    processing_time = models.FloatField(null=True, blank=True)  # Time in seconds
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'poster_generation_jobs'
        verbose_name = 'Poster Generation Job'
        verbose_name_plural = 'Poster Generation Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Poster Job {self.id} - {self.status}"
    
    def mark_processing(self):
        """Mark job as processing"""
        self.status = 'processing'
        self.save(update_fields=['status'])
    
    def mark_completed(self, generated_images=None, processing_time=None, cost=None):
        """Mark job as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if generated_images:
            self.generated_images = generated_images
            if generated_images:
                self.thumbnail_url = generated_images[0]  # Use first image as thumbnail
        if processing_time:
            self.processing_time = processing_time
        if cost:
            self.cost = cost
        self.save(update_fields=['status', 'completed_at', 'generated_images', 'thumbnail_url', 'processing_time', 'cost'])
    
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


class PosterTemplate(TenantScopedModel):
    """Model to store poster templates"""
    
    CATEGORY_CHOICES = [
        ('textile', 'Textile Design'),
        ('fashion', 'Fashion'),
        ('festival', 'Festival'),
        ('business', 'Business'),
        ('creative', 'Creative'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    # Template configuration
    prompt_template = models.TextField()
    negative_prompt_template = models.TextField(blank=True)
    default_parameters = models.JSONField(default=dict, blank=True)
    
    # Template preview
    preview_image = models.ImageField(upload_to='poster_templates/previews/', blank=True, null=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_poster_templates')
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'poster_templates'
        verbose_name = 'Poster Template'
        verbose_name_plural = 'Poster Templates'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['organization', 'category']),
            models.Index(fields=['is_public', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
    
    def increment_usage(self):
        """Increment usage counter"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class PosterGenerationHistory(TenantScopedModel):
    """Model to store generation history for analytics"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poster_history')
    job = models.OneToOneField(PosterGenerationJob, on_delete=models.CASCADE, related_name='history')
    
    # Analytics data
    user_satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating
    user_feedback = models.TextField(blank=True)
    regeneration_count = models.IntegerField(default=0)
    final_selection = models.CharField(max_length=500, blank=True)  # URL of selected result
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Use tenant-scoped manager
    objects = TenantScopedManager()
    
    class Meta:
        db_table = 'poster_generation_history'
        verbose_name = 'Poster Generation History'
        verbose_name_plural = 'Poster Generation Histories'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"History for {self.job}"