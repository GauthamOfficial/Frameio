from rest_framework import serializers
from .models import (
    AIProvider, AIGenerationRequest, AIUsageQuota, 
    AITemplate, AIGenerationHistory
)
from .scheduling_models import ScheduledPost


class AIProviderSerializer(serializers.ModelSerializer):
    """Serializer for AI Provider model"""
    
    class Meta:
        model = AIProvider
        fields = [
            'id', 'name', 'is_active', 'rate_limit_per_minute', 
            'rate_limit_per_hour', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """Custom representation to hide sensitive data"""
        data = super().to_representation(instance)
        # Don't expose API keys in responses
        return data


class AIGenerationRequestSerializer(serializers.ModelSerializer):
    """Serializer for AI Generation Request model"""
    provider_name = serializers.CharField(source='provider.get_name_display', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = AIGenerationRequest
        fields = [
            'id', 'organization', 'user', 'provider', 'provider_name', 'user_email',
            'generation_type', 'status', 'prompt', 'negative_prompt', 'parameters',
            'result_data', 'result_urls', 'error_message', 'processing_time', 'cost',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'organization', 'user', 'provider_name', 'user_email',
            'result_data', 'result_urls', 'error_message', 'processing_time', 
            'cost', 'created_at', 'updated_at', 'completed_at'
        ]
    
    def validate_prompt(self, value):
        """Validate prompt is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Prompt cannot be empty")
        return value.strip()
    
    def validate_parameters(self, value):
        """Validate parameters are valid JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Parameters must be a valid JSON object")
        return value


class AIGenerationRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating AI Generation Requests"""
    
    class Meta:
        model = AIGenerationRequest
        fields = [
            'provider', 'generation_type', 'prompt', 'negative_prompt', 'parameters'
        ]
    
    def validate_prompt(self, value):
        """Validate prompt is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Prompt cannot be empty")
        return value.strip()


class AIUsageQuotaSerializer(serializers.ModelSerializer):
    """Serializer for AI Usage Quota model"""
    provider_name = serializers.CharField(source='provider.get_name_display', read_only=True)
    usage_percentage = serializers.SerializerMethodField()
    cost_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = AIUsageQuota
        fields = [
            'id', 'organization', 'provider', 'provider_name', 'generation_type',
            'quota_type', 'max_requests', 'max_cost', 'current_requests', 
            'current_cost', 'usage_percentage', 'cost_percentage', 'reset_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'organization', 'provider_name', 'current_requests', 
            'current_cost', 'usage_percentage', 'cost_percentage',
            'created_at', 'updated_at'
        ]
    
    def get_usage_percentage(self, obj):
        """Calculate usage percentage"""
        if obj.max_requests == 0:
            return 0
        return round((obj.current_requests / obj.max_requests) * 100, 2)
    
    def get_cost_percentage(self, obj):
        """Calculate cost percentage"""
        if obj.max_cost == 0:
            return 0
        return round((float(obj.current_cost) / float(obj.max_cost)) * 100, 2)


class AITemplateSerializer(serializers.ModelSerializer):
    """Serializer for AI Template model"""
    
    class Meta:
        model = AITemplate
        fields = [
            'id', 'organization', 'name', 'description', 'category',
            'prompt_template', 'negative_prompt_template', 'default_parameters',
            'usage_count', 'is_public', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'organization', 'usage_count', 'created_at', 'updated_at']
    
    def validate_prompt_template(self, value):
        """Validate prompt template is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Prompt template cannot be empty")
        return value.strip()
    
    def validate_default_parameters(self, value):
        """Validate default parameters are valid JSON"""
        if not isinstance(value, dict):
            raise serializers.ValidationError("Default parameters must be a valid JSON object")
        return value


class AITemplatePublicSerializer(serializers.ModelSerializer):
    """Serializer for public AI Templates (limited fields)"""
    
    class Meta:
        model = AITemplate
        fields = [
            'id', 'name', 'description', 'category', 'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'name', 'description', 'category', 'usage_count', 'created_at']


class AIGenerationHistorySerializer(serializers.ModelSerializer):
    """Serializer for AI Generation History model"""
    request_details = AIGenerationRequestSerializer(source='request', read_only=True)
    
    class Meta:
        model = AIGenerationHistory
        fields = [
            'id', 'organization', 'user', 'request', 'request_details',
            'user_satisfaction_rating', 'user_feedback', 'regeneration_count',
            'final_selection', 'created_at'
        ]
        read_only_fields = [
            'id', 'organization', 'user', 'request', 'request_details', 'created_at'
        ]
    
    def validate_user_satisfaction_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class AIAnalyticsSerializer(serializers.Serializer):
    """Serializer for AI analytics data"""
    total_requests = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    failed_requests = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_processing_time = serializers.FloatField()
    total_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    most_used_generation_type = serializers.CharField()
    most_used_provider = serializers.CharField()
    quota_usage_by_type = serializers.DictField()


# Textile-specific serializers for Phase 1 Week 3
class TextilePosterRequestSerializer(serializers.Serializer):
    """Serializer for textile poster generation requests"""
    product_image_url = serializers.URLField(help_text="URL of the product image")
    fabric_type = serializers.ChoiceField(
        choices=[
            ('saree', 'Saree'),
            ('cotton', 'Cotton'),
            ('silk', 'Silk'),
            ('linen', 'Linen'),
            ('wool', 'Wool'),
            ('denim', 'Denim')
        ],
        help_text="Type of fabric"
    )
    festival = serializers.ChoiceField(
        choices=[
            ('deepavali', 'Deepavali'),
            ('pongal', 'Pongal'),
            ('wedding', 'Wedding'),
            ('general', 'General')
        ],
        help_text="Festival or occasion"
    )
    price_range = serializers.CharField(
        max_length=50,
        help_text="Price range (e.g., ₹2999)"
    )
    style = serializers.ChoiceField(
        choices=[
            ('elegant', 'Elegant'),
            ('modern', 'Modern'),
            ('traditional', 'Traditional'),
            ('bohemian', 'Bohemian'),
            ('casual', 'Casual')
        ],
        help_text="Design style"
    )
    color_scheme = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Color scheme description"
    )
    custom_text = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Custom text to include in poster"
    )
    offer_details = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Special offer details"
    )


class TextilePosterResponseSerializer(serializers.Serializer):
    """Serializer for textile poster generation responses"""
    success = serializers.BooleanField()
    poster_url = serializers.URLField()
    caption_suggestions = serializers.ListField(
        child=serializers.CharField(),
        help_text="AI-generated caption suggestions"
    )
    hashtags = serializers.ListField(
        child=serializers.CharField(),
        help_text="Relevant hashtags"
    )
    metadata = serializers.DictField()


class TextileCaptionRequestSerializer(serializers.Serializer):
    """Serializer for textile caption generation requests"""
    product_name = serializers.CharField(
        max_length=200,
        help_text="Name of the product"
    )
    fabric_type = serializers.ChoiceField(
        choices=[
            ('saree', 'Saree'),
            ('cotton', 'Cotton'),
            ('silk', 'Silk'),
            ('linen', 'Linen'),
            ('wool', 'Wool'),
            ('denim', 'Denim')
        ],
        help_text="Type of fabric"
    )
    festival = serializers.ChoiceField(
        choices=[
            ('deepavali', 'Deepavali'),
            ('pongal', 'Pongal'),
            ('wedding', 'Wedding'),
            ('general', 'General')
        ],
        required=False,
        help_text="Festival or occasion"
    )
    price_range = serializers.CharField(
        max_length=50,
        help_text="Price range (e.g., ₹2999)"
    )
    style = serializers.ChoiceField(
        choices=[
            ('elegant', 'Elegant'),
            ('modern', 'Modern'),
            ('traditional', 'Traditional'),
            ('bohemian', 'Bohemian'),
            ('casual', 'Casual')
        ],
        help_text="Design style"
    )
    custom_text = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Custom text to include in caption"
    )
    offer_details = serializers.CharField(
        max_length=500,
        required=False,
        help_text="Special offer details"
    )


class TextileCaptionResponseSerializer(serializers.Serializer):
    """Serializer for textile caption generation responses"""
    success = serializers.BooleanField()
    captions = serializers.ListField(
        child=serializers.CharField(),
        help_text="AI-generated caption suggestions"
    )
    hashtags = serializers.ListField(
        child=serializers.CharField(),
        help_text="Relevant hashtags"
    )
    metadata = serializers.DictField()


# Scheduling system serializers
class ScheduledPostSerializer(serializers.ModelSerializer):
    """Serializer for ScheduledPost model"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    platform_display = serializers.CharField(source='get_platform_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ScheduledPost
        fields = [
            'id', 'organization', 'user', 'user_email', 'platform', 'platform_display',
            'asset_url', 'caption', 'scheduled_time', 'status', 'status_display',
            'created_at', 'updated_at', 'posted_at', 'error_message', 'retry_count',
            'max_retries', 'metadata'
        ]
        read_only_fields = [
            'id', 'organization', 'user', 'user_email', 'platform_display',
            'status_display', 'created_at', 'updated_at', 'posted_at',
            'error_message', 'retry_count'
        ]


class ScheduledPostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating scheduled posts"""
    
    class Meta:
        model = ScheduledPost
        fields = [
            'platform', 'asset_url', 'caption', 'scheduled_time', 'metadata'
        ]
    
    def validate_scheduled_time(self, value):
        """Validate scheduled time is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value
    
    def validate_platform(self, value):
        """Validate platform is supported"""
        supported_platforms = [choice[0] for choice in ScheduledPost.PLATFORM_CHOICES]
        if value not in supported_platforms:
            raise serializers.ValidationError(f"Unsupported platform: {value}")
        return value


class ScheduledPostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating scheduled posts"""
    
    class Meta:
        model = ScheduledPost
        fields = [
            'platform', 'asset_url', 'caption', 'scheduled_time', 'metadata'
        ]
    
    def validate_scheduled_time(self, value):
        """Validate scheduled time is in the future"""
        from django.utils import timezone
        if value <= timezone.now():
            raise serializers.ValidationError("Scheduled time must be in the future")
        return value


# Social Media Posting serializers
class SocialMediaPostSerializer(serializers.Serializer):
    """Serializer for social media posting requests"""
    platform = serializers.ChoiceField(
        choices=[
            ('facebook', 'Facebook'),
            ('instagram', 'Instagram'),
            ('tiktok', 'TikTok'),
            ('whatsapp', 'WhatsApp'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn'),
        ],
        help_text="Social media platform"
    )
    asset_url = serializers.URLField(help_text="URL of the asset to post")
    caption = serializers.CharField(
        max_length=5000,
        help_text="Post caption"
    )
    metadata = serializers.DictField(
        required=False,
        help_text="Additional metadata for the post"
    )


class SocialMediaPostResponseSerializer(serializers.Serializer):
    """Serializer for social media posting responses"""
    success = serializers.BooleanField()
    platform = serializers.CharField()
    post_id = serializers.CharField(required=False)
    url = serializers.URLField(required=False)
    message = serializers.CharField()
    posted_at = serializers.DateTimeField()
    organization = serializers.CharField()


# Catalog Builder serializers
class CatalogCreateRequestSerializer(serializers.Serializer):
    """Serializer for catalog creation requests"""
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="List of product IDs to include in catalog"
    )
    template = serializers.ChoiceField(
        choices=[
            ('festival_collection', 'Festival Collection'),
            ('wedding_collection', 'Wedding Collection'),
            ('casual_wear', 'Casual Wear'),
            ('premium_collection', 'Premium Collection'),
        ],
        help_text="Catalog template"
    )
    style = serializers.ChoiceField(
        choices=[
            ('modern', 'Modern'),
            ('traditional', 'Traditional'),
            ('elegant', 'Elegant'),
            ('bohemian', 'Bohemian'),
        ],
        help_text="Design style"
    )
    color_scheme = serializers.CharField(
        max_length=100,
        help_text="Color scheme for the catalog"
    )


class CatalogCreateResponseSerializer(serializers.Serializer):
    """Serializer for catalog creation responses"""
    success = serializers.BooleanField()
    catalog_url = serializers.URLField()
    catalog_name = serializers.CharField()
    created_at = serializers.DateTimeField()
    organization = serializers.CharField()
