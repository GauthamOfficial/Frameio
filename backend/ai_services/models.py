from django.db import models
from django.contrib.auth import get_user_model
from organizations.models import Organization
import uuid
from django.utils import timezone

User = get_user_model()


class AIProvider(models.Model):
    """Model to store AI service provider configurations"""
    PROVIDER_CHOICES = [
        ('gemini', 'Google Gemini'),
        ('openai', 'OpenAI'),
        ('stability', 'Stability AI'),
        ('midjourney', 'Midjourney'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, choices=PROVIDER_CHOICES)
    api_key = models.CharField(max_length=500, blank=True, null=True)
    api_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    rate_limit_per_minute = models.IntegerField(default=60)
    rate_limit_per_hour = models.IntegerField(default=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name']
    
    def __str__(self):
        return f"{self.get_name_display()} - {'Active' if self.is_active else 'Inactive'}"


class AIGenerationRequest(models.Model):
    """Model to track AI generation requests"""
    GENERATION_TYPES = [
        ('text_generation', 'Text Generation'),
        ('content_analysis', 'Content Analysis'),
        ('data_processing', 'Data Processing'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_requests')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    generation_type = models.CharField(max_length=50, choices=GENERATION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Request parameters
    prompt = models.TextField()
    negative_prompt = models.TextField(blank=True, null=True)
    parameters = models.JSONField(default=dict, blank=True)  # Store additional parameters
    
    # Response data
    result_data = models.JSONField(default=dict, blank=True)
    result_text = models.TextField(blank=True, null=True)  # Store generated text content
    error_message = models.TextField(blank=True, null=True)
    
    # Metadata
    processing_time = models.FloatField(null=True, blank=True)  # Time in seconds
    cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['user', 'generation_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.generation_type} - {self.status} ({self.organization.name})"
    
    def mark_completed(self, result_data=None, result_text=None):
        """Mark the request as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        if result_data:
            self.result_data = result_data
        if result_text:
            self.result_text = result_text
        self.save(update_fields=['status', 'completed_at', 'result_data', 'result_text'])
    
    def mark_failed(self, error_message):
        """Mark the request as failed"""
        self.status = 'failed'
        self.error_message = error_message
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'error_message', 'completed_at'])


class AIUsageQuota(models.Model):
    """Model to manage AI usage quotas per organization"""
    QUOTA_TYPES = [
        ('monthly', 'Monthly'),
        ('daily', 'Daily'),
        ('hourly', 'Hourly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_quotas')
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    generation_type = models.CharField(max_length=50, choices=AIGenerationRequest.GENERATION_TYPES)
    quota_type = models.CharField(max_length=20, choices=QUOTA_TYPES)
    
    # Quota limits
    max_requests = models.IntegerField(default=100)
    max_cost = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)
    
    # Current usage
    current_requests = models.IntegerField(default=0)
    current_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Reset information
    reset_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['organization', 'provider', 'generation_type', 'quota_type']
        indexes = [
            models.Index(fields=['organization', 'quota_type']),
            models.Index(fields=['reset_at']),
        ]
    
    def __str__(self):
        return f"{self.organization.name} - {self.generation_type} ({self.quota_type})"
    
    def is_quota_exceeded(self):
        """Check if quota is exceeded"""
        return (self.current_requests >= self.max_requests or 
                self.current_cost >= self.max_cost)
    
    def increment_usage(self, cost=0):
        """Increment usage counters"""
        self.current_requests += 1
        self.current_cost += cost
        self.save(update_fields=['current_requests', 'current_cost'])
    
    def reset_usage(self):
        """Reset usage counters"""
        self.current_requests = 0
        self.current_cost = 0
        self.save(update_fields=['current_requests', 'current_cost'])


class AITemplate(models.Model):
    """Model to store AI generation templates and prompts"""
    TEMPLATE_CATEGORIES = [
        ('text_generation', 'Text Generation'),
        ('content_analysis', 'Content Analysis'),
        ('data_processing', 'Data Processing'),
        ('reporting', 'Report Generation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_templates', null=True, blank=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=TEMPLATE_CATEGORIES)
    
    # Template configuration
    prompt_template = models.TextField()
    negative_prompt_template = models.TextField(blank=True)
    default_parameters = models.JSONField(default=dict, blank=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)  # Public templates available to all orgs
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
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


class AIGenerationHistory(models.Model):
    """Model to store generation history for analytics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='ai_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_history')
    request = models.OneToOneField(AIGenerationRequest, on_delete=models.CASCADE, related_name='history')
    
    # Analytics data
    user_satisfaction_rating = models.IntegerField(null=True, blank=True)  # 1-5 rating
    user_feedback = models.TextField(blank=True)
    regeneration_count = models.IntegerField(default=0)
    final_selection = models.TextField(blank=True)  # Text content of selected result
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"History for {self.request}"


# Import scheduling models
from .scheduling_models import ScheduledPost


class GeneratedPoster(models.Model):
    """Model to store generated posters with captions and metadata"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='generated_posters', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_posters', null=True, blank=True)
    
    # Poster details
    image_url = models.URLField(help_text="URL of the generated poster image")
    image_path = models.CharField(max_length=500, blank=True, help_text="Storage path of the image")
    caption = models.TextField(help_text="Short caption for the poster")
    full_caption = models.TextField(blank=True, help_text="Full caption with hashtags")
    prompt = models.TextField(help_text="Original prompt used to generate the poster")
    
    # Metadata
    aspect_ratio = models.CharField(max_length=20, default='1:1', help_text="Aspect ratio of the poster")
    width = models.IntegerField(null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    hashtags = models.JSONField(default=list, blank=True, help_text="List of hashtags")
    emoji = models.CharField(max_length=50, blank=True)
    call_to_action = models.TextField(blank=True)
    
    # Branding information
    branding_applied = models.BooleanField(default=False)
    logo_added = models.BooleanField(default=False)
    contact_info_added = models.BooleanField(default=False)
    branding_metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Poster - {self.prompt[:50]}... ({self.created_at.strftime('%Y-%m-%d')})"


class GeneratedBrandingKit(models.Model):
    """Model to store generated branding kits with logo and color palette"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='generated_branding_kits', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generated_branding_kits', null=True, blank=True)
    
    # Branding kit details
    prompt = models.TextField(help_text="Original prompt used to generate the branding kit")
    style = models.CharField(max_length=50, default='modern', help_text="Style used for generation")
    
    # Logo data (stored as base64 or URL)
    logo_data = models.TextField(blank=True, help_text="Base64 encoded logo image")
    logo_format = models.CharField(max_length=10, default='png', help_text="Logo image format")
    logo_url = models.URLField(blank=True, null=True, help_text="URL of the logo if stored externally")
    
    # Color palette data
    color_palette_data = models.TextField(blank=True, help_text="Base64 encoded color palette image")
    color_palette_format = models.CharField(max_length=10, default='png', help_text="Color palette image format")
    color_palette_url = models.URLField(blank=True, null=True, help_text="URL of the color palette if stored externally")
    colors = models.JSONField(default=list, blank=True, help_text="List of hex color codes")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Branding Kit - {self.prompt[:50]}... ({self.created_at.strftime('%Y-%m-%d')})"