from rest_framework import serializers
from .models import ExportJob, ExportTemplate, ExportHistory
from django.contrib.auth import get_user_model

User = get_user_model()


class ExportJobSerializer(serializers.ModelSerializer):
    """Serializer for ExportJob"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = ExportJob
        fields = [
            'id', 'user', 'user_name', 'user_email', 'organization_name',
            'status', 'design_ids', 'export_format', 'export_options',
            'export_file_path', 'download_url', 'file_size', 'processing_time',
            'error_message', 'created_at', 'updated_at', 'completed_at',
            'expires_at', 'is_expired'
        ]
        read_only_fields = [
            'id', 'user', 'organization', 'status', 'export_file_path',
            'download_url', 'file_size', 'processing_time', 'error_message',
            'created_at', 'updated_at', 'completed_at', 'expires_at'
        ]


class ExportJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating ExportJob"""
    
    class Meta:
        model = ExportJob
        fields = [
            'design_ids', 'export_format', 'export_options'
        ]
    
    def validate_design_ids(self, value):
        """Validate design IDs"""
        if not value or not isinstance(value, list):
            raise serializers.ValidationError("design_ids must be a non-empty list")
        
        if len(value) > 50:  # Limit batch size
            raise serializers.ValidationError("Cannot export more than 50 designs at once")
        
        return value
    
    def validate_export_format(self, value):
        """Validate export format"""
        valid_formats = [choice[0] for choice in ExportJob.EXPORT_FORMAT_CHOICES]
        if value not in valid_formats:
            raise serializers.ValidationError(f"Invalid export format. Must be one of: {valid_formats}")
        
        return value


class ExportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ExportTemplate"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'export_format',
            'export_options', 'layout_config', 'usage_count', 'is_public',
            'is_active', 'created_at', 'updated_at', 'created_by',
            'created_by_name', 'organization_name'
        ]
        read_only_fields = [
            'id', 'usage_count', 'created_at', 'updated_at', 'created_by', 'organization'
        ]


class ExportTemplatePublicSerializer(serializers.ModelSerializer):
    """Public serializer for ExportTemplate (without sensitive data)"""
    
    class Meta:
        model = ExportTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'export_format',
            'export_options', 'layout_config', 'usage_count', 'is_public',
            'created_at'
        ]


class ExportHistorySerializer(serializers.ModelSerializer):
    """Serializer for ExportHistory"""
    
    export_job = ExportJobSerializer(read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ExportHistory
        fields = [
            'id', 'user', 'user_name', 'export_job', 'download_count',
            'user_feedback', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'export_job', 'created_at']


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for export request"""
    
    design_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=50
    )
    export_format = serializers.ChoiceField(
        choices=ExportJob.EXPORT_FORMAT_CHOICES,
        default='png'
    )
    export_options = serializers.JSONField(required=False, default=dict)
    template_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """Validate the request data"""
        # If template_id is provided, validate it exists and is accessible
        template_id = data.get('template_id')
        if template_id:
            try:
                template = ExportTemplate.objects.get(id=template_id, is_active=True)
                # Check if template is public or belongs to current organization
                if not template.is_public and template.organization != self.context.get('organization'):
                    raise serializers.ValidationError("Template not accessible")
            except ExportTemplate.DoesNotExist:
                raise serializers.ValidationError("Template not found")
        
        return data


class ExportStatusSerializer(serializers.Serializer):
    """Serializer for export status response"""
    
    job_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.IntegerField(min_value=0, max_value=100)
    message = serializers.CharField()
    download_url = serializers.URLField(required=False)
    file_size = serializers.IntegerField(required=False)
    expires_at = serializers.DateTimeField(required=False)
    error_message = serializers.CharField(required=False)


class DownloadRequestSerializer(serializers.Serializer):
    """Serializer for download request"""
    
    job_id = serializers.UUIDField()
    
    def validate_job_id(self, value):
        """Validate job ID and check permissions"""
        try:
            job = ExportJob.objects.get(id=value)
            
            # Check if job belongs to current user or organization
            organization = self.context.get('organization')
            user = self.context.get('user')
            
            if job.organization != organization:
                raise serializers.ValidationError("Job not found")
            
            if job.user != user and not user.is_staff:
                raise serializers.ValidationError("Access denied")
            
            # Check if job is completed
            if job.status != 'completed':
                raise serializers.ValidationError("Export job not completed")
            
            # Check if download link has expired
            if job.is_expired():
                raise serializers.ValidationError("Download link has expired")
            
            return value
            
        except ExportJob.DoesNotExist:
            raise serializers.ValidationError("Export job not found")
