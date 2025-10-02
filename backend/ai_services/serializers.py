from rest_framework import serializers
from .models import (
    AIProvider, AIGenerationRequest, AIUsageQuota, 
    AITemplate, AIGenerationHistory
)


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
