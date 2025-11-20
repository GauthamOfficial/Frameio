from rest_framework import serializers
from .models import (
    DesignShare, DesignComment, DesignCollaboration, 
    DesignVersion, DesignActivity
)
from django.contrib.auth import get_user_model

User = get_user_model()


class DesignShareSerializer(serializers.ModelSerializer):
    """Serializer for DesignShare"""
    
    shared_by_name = serializers.CharField(source='shared_by.get_full_name', read_only=True)
    shared_with_name = serializers.CharField(source='shared_with.get_full_name', read_only=True)
    design_title = serializers.CharField(source='design.title', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DesignShare
        fields = [
            'id', 'design', 'design_title', 'shared_by', 'shared_by_name',
            'shared_with', 'shared_with_name', 'access_level', 'status',
            'share_token', 'is_public', 'allow_download', 'allow_comments',
            'expires_at', 'message', 'created_at', 'updated_at',
            'organization_name', 'is_expired'
        ]
        read_only_fields = [
            'id', 'shared_by', 'share_token', 'created_at', 'updated_at'
        ]


class DesignShareCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DesignShare"""
    
    class Meta:
        model = DesignShare
        fields = [
            'design', 'shared_with', 'access_level', 'is_public',
            'allow_download', 'allow_comments', 'expires_at', 'message'
        ]
    
    def validate(self, data):
        """Validate the share data"""
        design = data.get('design')
        shared_with = data.get('shared_with')
        is_public = data.get('is_public', False)
        
        # If not public, shared_with is required
        if not is_public and not shared_with:
            raise serializers.ValidationError("shared_with is required for private shares")
        
        # If public, shared_with should not be provided
        if is_public and shared_with:
            raise serializers.ValidationError("shared_with should not be provided for public shares")
        
        # Check if user has permission to share this design
        user = self.context['request'].user
        if not design.can_be_edited_by(user):
            raise serializers.ValidationError("You don't have permission to share this design")
        
        return data


class DesignCommentSerializer(serializers.ModelSerializer):
    """Serializer for DesignComment"""
    
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.CharField(source='author.email', read_only=True)
    design_title = serializers.CharField(source='design.title', read_only=True)
    replies_count = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignComment
        fields = [
            'id', 'design', 'design_title', 'author', 'author_name', 'author_email',
            'parent_comment', 'content', 'is_resolved', 'created_at', 'updated_at',
            'replies_count', 'can_edit', 'can_delete'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
    
    def get_replies_count(self, obj):
        """Get count of replies to this comment"""
        return obj.replies.count()
    
    def get_can_edit(self, obj):
        """Check if current user can edit this comment"""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_edit(request.user)
        return False
    
    def get_can_delete(self, obj):
        """Check if current user can delete this comment"""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_delete(request.user)
        return False


class DesignCommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating DesignComment"""
    
    class Meta:
        model = DesignComment
        fields = ['design', 'parent_comment', 'content']
    
    def validate(self, data):
        """Validate the comment data"""
        design = data.get('design')
        parent_comment = data.get('parent_comment')
        
        # If parent_comment is provided, validate it belongs to the same design
        if parent_comment and parent_comment.design != design:
            raise serializers.ValidationError("Parent comment must belong to the same design")
        
        return data


class DesignCollaborationSerializer(serializers.ModelSerializer):
    """Serializer for DesignCollaboration"""
    
    initiator_name = serializers.CharField(source='initiator.get_full_name', read_only=True)
    design_title = serializers.CharField(source='design.title', read_only=True)
    participants_count = serializers.SerializerMethodField()
    participants_names = serializers.SerializerMethodField()
    can_join = serializers.SerializerMethodField()
    
    class Meta:
        model = DesignCollaboration
        fields = [
            'id', 'design', 'design_title', 'initiator', 'initiator_name',
            'participants', 'participants_count', 'participants_names',
            'status', 'allow_edit', 'allow_comments', 'auto_save',
            'session_data', 'started_at', 'last_activity', 'ended_at',
            'can_join'
        ]
        read_only_fields = [
            'id', 'initiator', 'started_at', 'last_activity', 'ended_at'
        ]
    
    def get_participants_count(self, obj):
        """Get count of participants"""
        return obj.participants.count()
    
    def get_participants_names(self, obj):
        """Get names of participants"""
        return [participant.get_full_name() for participant in obj.participants.all()]
    
    def get_can_join(self, obj):
        """Check if current user can join this collaboration"""
        request = self.context.get('request')
        if request and request.user:
            return obj.can_join(request.user)
        return False


class DesignVersionSerializer(serializers.ModelSerializer):
    """Serializer for DesignVersion"""
    
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    design_title = serializers.CharField(source='design.title', read_only=True)
    collaboration_title = serializers.CharField(source='collaboration.design.title', read_only=True)
    
    class Meta:
        model = DesignVersion
        fields = [
            'id', 'design', 'design_title', 'version_number', 'created_by',
            'created_by_name', 'collaboration', 'collaboration_title',
            'version_data', 'changes_summary', 'image', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']


class DesignActivitySerializer(serializers.ModelSerializer):
    """Serializer for DesignActivity"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    design_title = serializers.CharField(source='design.title', read_only=True)
    
    class Meta:
        model = DesignActivity
        fields = [
            'id', 'design', 'design_title', 'user', 'user_name',
            'activity_type', 'activity_data', 'description',
            'related_comment', 'related_collaboration', 'related_version',
            'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class ShareDesignRequestSerializer(serializers.Serializer):
    """Serializer for sharing design request"""
    
    design_id = serializers.UUIDField()
    shared_with_email = serializers.EmailField(required=False)
    access_level = serializers.ChoiceField(
        choices=DesignShare.ACCESS_LEVEL_CHOICES,
        default='view'
    )
    is_public = serializers.BooleanField(default=False)
    allow_download = serializers.BooleanField(default=False)
    allow_comments = serializers.BooleanField(default=True)
    expires_at = serializers.DateTimeField(required=False)
    message = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate the share request"""
        shared_with_email = data.get('shared_with_email')
        is_public = data.get('is_public', False)
        
        # If not public, shared_with_email is required
        if not is_public and not shared_with_email:
            raise serializers.ValidationError("shared_with_email is required for private shares")
        
        # If public, shared_with_email should not be provided
        if is_public and shared_with_email:
            raise serializers.ValidationError("shared_with_email should not be provided for public shares")
        
        return data


class InviteMemberRequestSerializer(serializers.Serializer):
    """Serializer for inviting member to collaboration"""
    
    email = serializers.EmailField()
    access_level = serializers.ChoiceField(
        choices=DesignShare.ACCESS_LEVEL_CHOICES,
        default='view'
    )
    message = serializers.CharField(required=False, allow_blank=True)


class UpdateAccessRequestSerializer(serializers.Serializer):
    """Serializer for updating access level"""
    
    share_id = serializers.UUIDField()
    access_level = serializers.ChoiceField(choices=DesignShare.ACCESS_LEVEL_CHOICES)
    allow_download = serializers.BooleanField(required=False)
    allow_comments = serializers.BooleanField(required=False)


class CollaborationJoinRequestSerializer(serializers.Serializer):
    """Serializer for joining collaboration"""
    
    collaboration_id = serializers.UUIDField()
    
    def validate_collaboration_id(self, value):
        """Validate collaboration ID"""
        try:
            collaboration = DesignCollaboration.objects.get(id=value)
            if collaboration.status != 'active':
                raise serializers.ValidationError("Collaboration is not active")
            return value
        except DesignCollaboration.DoesNotExist:
            raise serializers.ValidationError("Collaboration not found")


class CommentCreateRequestSerializer(serializers.Serializer):
    """Serializer for creating comment request"""
    
    design_id = serializers.UUIDField()
    content = serializers.CharField()
    parent_comment_id = serializers.UUIDField(required=False)
    
    def validate(self, data):
        """Validate the comment request"""
        design_id = data.get('design_id')
        parent_comment_id = data.get('parent_comment_id')
        
        # If parent_comment_id is provided, validate it belongs to the same design
        if parent_comment_id:
            try:
                from .models import DesignComment
                parent_comment = DesignComment.objects.get(id=parent_comment_id)
                if parent_comment.design.id != design_id:
                    raise serializers.ValidationError("Parent comment must belong to the same design")
            except DesignComment.DoesNotExist:
                raise serializers.ValidationError("Parent comment not found")
        
        return data
