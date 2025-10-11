"""
Serializers for AI Post Generation
"""
from rest_framework import serializers
from .models import AIGenerationRequest


class AIPostGenerationSerializer(serializers.Serializer):
    """Serializer for AI post generation requests"""
    
    # Required fields
    prompt = serializers.CharField(max_length=1000, help_text="Base prompt for the post")
    
    # Optional fields
    post_type = serializers.ChoiceField(
        choices=[
            ('social_media', 'Social Media'),
            ('blog', 'Blog'),
            ('announcement', 'Announcement'),
            ('promotional', 'Promotional'),
            ('educational', 'Educational')
        ],
        default='social_media',
        help_text="Type of post to generate"
    )
    
    style = serializers.ChoiceField(
        choices=[
            ('modern', 'Modern'),
            ('traditional', 'Traditional'),
            ('casual', 'Casual'),
            ('formal', 'Formal')
        ],
        default='modern',
        help_text="Writing style for the post"
    )
    
    tone = serializers.ChoiceField(
        choices=[
            ('professional', 'Professional'),
            ('friendly', 'Friendly'),
            ('authoritative', 'Authoritative'),
            ('conversational', 'Conversational')
        ],
        default='professional',
        help_text="Tone of voice for the post"
    )
    
    length = serializers.ChoiceField(
        choices=[
            ('short', 'Short'),
            ('medium', 'Medium'),
            ('long', 'Long')
        ],
        default='medium',
        help_text="Length of the post"
    )
    
    include_hashtags = serializers.BooleanField(
        default=True,
        help_text="Whether to include hashtags in the post"
    )
    
    include_emoji = serializers.BooleanField(
        default=True,
        help_text="Whether to include emojis in the post"
    )
    
    # Platform-specific fields
    platform = serializers.ChoiceField(
        choices=[
            ('instagram', 'Instagram'),
            ('facebook', 'Facebook'),
            ('twitter', 'Twitter'),
            ('linkedin', 'LinkedIn')
        ],
        required=False,
        help_text="Social media platform for optimization"
    )
    
    # Image-related fields
    images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        help_text="Images to include with the post"
    )
    
    # Additional customization
    custom_hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="Custom hashtags to include"
    )
    
    target_audience = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Target audience for the post"
    )
    
    call_to_action = serializers.CharField(
        max_length=200,
        required=False,
        help_text="Custom call to action"
    )


class AIPostContentSerializer(serializers.Serializer):
    """Serializer for AI-generated post content"""
    
    main_content = serializers.CharField(help_text="Main post content")
    hashtags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        help_text="Generated hashtags"
    )
    call_to_action = serializers.CharField(help_text="Call to action text")
    word_count = serializers.IntegerField(help_text="Word count of the post")
    character_count = serializers.IntegerField(help_text="Character count of the post")
    post_type = serializers.CharField(help_text="Type of post generated")
    engagement_score = serializers.FloatField(help_text="Predicted engagement score")
    
    # Optional fields
    generated_images = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Generated images (if any)"
    )


class AIPostGenerationResponseSerializer(serializers.Serializer):
    """Serializer for AI post generation API responses"""
    
    success = serializers.BooleanField(help_text="Whether the generation was successful")
    content = AIPostContentSerializer(help_text="Generated post content")
    request_id = serializers.UUIDField(help_text="Unique request identifier")
    metadata = serializers.DictField(help_text="Generation metadata")
    
    # Error fields
    error = serializers.CharField(
        required=False,
        help_text="Error message if generation failed"
    )


class AIPostTemplateSerializer(serializers.Serializer):
    """Serializer for AI post templates"""
    
    id = serializers.CharField(help_text="Template identifier")
    name = serializers.CharField(help_text="Template name")
    description = serializers.CharField(help_text="Template description")
    post_type = serializers.CharField(help_text="Post type for this template")
    style = serializers.CharField(help_text="Writing style for this template")
    tone = serializers.CharField(help_text="Tone for this template")
    length = serializers.CharField(help_text="Length for this template")
    
    # Optional fields
    platform = serializers.CharField(
        required=False,
        help_text="Target platform for this template"
    )
    example_prompt = serializers.CharField(
        required=False,
        help_text="Example prompt for this template"
    )
    usage_count = serializers.IntegerField(
        required=False,
        help_text="Number of times this template has been used"
    )


class AIServiceStatusSerializer(serializers.Serializer):
    """Serializer for AI service status"""
    
    success = serializers.BooleanField(help_text="Whether the request was successful")
    service_available = serializers.BooleanField(help_text="Whether the AI service is available")
    fallback_mode = serializers.BooleanField(help_text="Whether the service is in fallback mode")
    service_name = serializers.CharField(help_text="Name of the AI service")
    version = serializers.CharField(help_text="Version of the AI service")
    
    # Optional fields
    error_message = serializers.CharField(
        required=False,
        help_text="Error message if service is unavailable"
    )
    last_updated = serializers.DateTimeField(
        required=False,
        help_text="Last time the service was updated"
    )


class AIPostAnalyticsSerializer(serializers.Serializer):
    """Serializer for AI post generation analytics"""
    
    total_posts_generated = serializers.IntegerField(help_text="Total number of posts generated")
    successful_generations = serializers.IntegerField(help_text="Number of successful generations")
    failed_generations = serializers.IntegerField(help_text="Number of failed generations")
    success_rate = serializers.FloatField(help_text="Success rate percentage")
    average_engagement_score = serializers.FloatField(help_text="Average engagement score")
    most_used_post_type = serializers.CharField(help_text="Most frequently used post type")
    most_used_style = serializers.CharField(help_text="Most frequently used style")
    most_used_tone = serializers.CharField(help_text="Most frequently used tone")
    
    # Time-based analytics
    posts_generated_today = serializers.IntegerField(help_text="Posts generated today")
    posts_generated_this_week = serializers.IntegerField(help_text="Posts generated this week")
    posts_generated_this_month = serializers.IntegerField(help_text="Posts generated this month")
    
    # Cost analytics
    total_cost = serializers.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Total cost of AI generation"
    )
    average_cost_per_post = serializers.DecimalField(
        max_digits=10,
        decimal_places=4,
        help_text="Average cost per post"
    )
    
    # Platform analytics
    platform_breakdown = serializers.DictField(
        help_text="Breakdown of posts by platform"
    )
    
    # Engagement analytics
    high_engagement_posts = serializers.IntegerField(
        help_text="Number of posts with high engagement scores"
    )
    average_hashtag_count = serializers.FloatField(
        help_text="Average number of hashtags per post"
    )
    emoji_usage_rate = serializers.FloatField(
        help_text="Percentage of posts using emojis"
    )
