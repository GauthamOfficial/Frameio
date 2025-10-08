from rest_framework import serializers
from .models import PosterGenerationJob, PosterTemplate, PosterGenerationHistory
from django.contrib.auth import get_user_model

User = get_user_model()


class PosterGenerationJobSerializer(serializers.ModelSerializer):
    """Serializer for PosterGenerationJob"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PosterGenerationJob
        fields = [
            'id', 'user', 'user_name', 'user_email', 'organization_name',
            'status', 'prompt', 'negative_prompt', 'design_metadata',
            'width', 'height', 'num_images', 'guidance_scale', 'num_inference_steps',
            'generated_images', 'thumbnail_url', 'processing_time', 'cost',
            'error_message', 'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user', 'organization', 'status', 'generated_images',
            'thumbnail_url', 'processing_time', 'cost', 'error_message',
            'created_at', 'updated_at', 'completed_at'
        ]


class PosterGenerationJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating PosterGenerationJob"""
    
    class Meta:
        model = PosterGenerationJob
        fields = [
            'prompt', 'negative_prompt', 'design_metadata',
            'width', 'height', 'num_images', 'guidance_scale', 'num_inference_steps'
        ]
    
    def validate_width(self, value):
        """Validate width"""
        if value < 256 or value > 2048:
            raise serializers.ValidationError("Width must be between 256 and 2048 pixels")
        return value
    
    def validate_height(self, value):
        """Validate height"""
        if value < 256 or value > 2048:
            raise serializers.ValidationError("Height must be between 256 and 2048 pixels")
        return value
    
    def validate_num_images(self, value):
        """Validate number of images"""
        if value < 1 or value > 4:
            raise serializers.ValidationError("Number of images must be between 1 and 4")
        return value
    
    def validate_guidance_scale(self, value):
        """Validate guidance scale"""
        if value < 1.0 or value > 20.0:
            raise serializers.ValidationError("Guidance scale must be between 1.0 and 20.0")
        return value
    
    def validate_num_inference_steps(self, value):
        """Validate number of inference steps"""
        if value < 10 or value > 100:
            raise serializers.ValidationError("Number of inference steps must be between 10 and 100")
        return value


class PosterTemplateSerializer(serializers.ModelSerializer):
    """Serializer for PosterTemplate"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = PosterTemplate
        fields = [
            'id', 'name', 'description', 'category', 'prompt_template',
            'negative_prompt_template', 'default_parameters', 'preview_image',
            'usage_count', 'is_public', 'is_active', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'organization_name'
        ]
        read_only_fields = [
            'id', 'usage_count', 'created_at', 'updated_at', 'created_by', 'organization'
        ]


class PosterTemplatePublicSerializer(serializers.ModelSerializer):
    """Public serializer for PosterTemplate (without sensitive data)"""
    
    class Meta:
        model = PosterTemplate
        fields = [
            'id', 'name', 'description', 'category', 'prompt_template',
            'negative_prompt_template', 'default_parameters', 'preview_image',
            'usage_count', 'is_public', 'created_at'
        ]


class PosterGenerationHistorySerializer(serializers.ModelSerializer):
    """Serializer for PosterGenerationHistory"""
    
    job = PosterGenerationJobSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = PosterGenerationHistory
        fields = [
            'id', 'user', 'user_name', 'job', 'user_satisfaction_rating',
            'user_feedback', 'regeneration_count', 'final_selection', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'job', 'created_at']


class PosterGenerationStatusSerializer(serializers.Serializer):
    """Serializer for poster generation status response"""
    
    job_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.IntegerField(min_value=0, max_value=100)
    message = serializers.CharField()
    generated_images = serializers.ListField(child=serializers.URLField(), required=False)
    error_message = serializers.CharField(required=False)
    estimated_completion = serializers.DateTimeField(required=False)


class PosterGenerationRequestSerializer(serializers.Serializer):
    """Serializer for poster generation request"""
    
    prompt = serializers.CharField(max_length=1000)
    negative_prompt = serializers.CharField(max_length=500, required=False, allow_blank=True)
    design_metadata = serializers.JSONField(required=False, default=dict)
    width = serializers.IntegerField(default=1024, min_value=256, max_value=2048)
    height = serializers.IntegerField(default=1024, min_value=256, max_value=2048)
    num_images = serializers.IntegerField(default=1, min_value=1, max_value=4)
    guidance_scale = serializers.FloatField(default=7.5, min_value=1.0, max_value=20.0)
    num_inference_steps = serializers.IntegerField(default=20, min_value=10, max_value=100)
    template_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """Validate the request data"""
        # If template_id is provided, validate it exists and is accessible
        template_id = data.get('template_id')
        if template_id:
            try:
                template = PosterTemplate.objects.get(id=template_id, is_active=True)
                # Check if template is public or belongs to current organization
                if not template.is_public and template.organization != self.context.get('organization'):
                    raise serializers.ValidationError("Template not accessible")
            except PosterTemplate.DoesNotExist:
                raise serializers.ValidationError("Template not found")
        
        return data
