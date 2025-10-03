"""
Serializers for user management and profiles.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserActivity
from organizations.models import OrganizationMember, Organization

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    current_organization_name = serializers.CharField(
        source='current_organization.name', 
        read_only=True
    )
    current_organization_role = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'user', 'user_email', 'user_name', 'user_avatar',
            'current_organization', 'current_organization_name', 'current_organization_role',
            'job_title', 'department', 'company_size',
            'email_notifications', 'push_notifications', 'marketing_emails',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.full_name or obj.user.username
    
    def get_current_organization_role(self, obj):
        """Get user's role in current organization."""
        return obj.get_current_organization_role()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    organizations = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'phone_number', 'bio', 'location', 'website',
            'timezone', 'language', 'theme', 'is_verified', 'last_active',
            'created_at', 'updated_at', 'profile', 'organizations'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_active', 'is_verified'
        ]
    
    def get_organizations(self, obj):
        """Get user's organizations."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization'):
            # Return only current organization for tenant-scoped requests
            return [{
                'id': str(request.organization.id),
                'name': request.organization.name,
                'slug': request.organization.slug,
                'role': obj.get_organization_role(request.organization)
            }]
        else:
            # Return all organizations for user profile requests
            return [
                {
                    'id': str(membership.organization.id),
                    'name': membership.organization.name,
                    'slug': membership.organization.slug,
                    'role': membership.role
                }
                for membership in obj.organization_memberships.filter(is_active=True)
            ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'avatar', 'phone_number', 
            'bio', 'location', 'website', 'timezone', 'language', 'theme'
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile details.
    """
    class Meta:
        model = UserProfile
        fields = [
            'job_title', 'department', 'company_size',
            'email_notifications', 'push_notifications', 'marketing_emails'
        ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for organization members (tenant-scoped).
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    joined_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_avatar',
            'user_first_name', 'user_last_name', 'role', 'is_active',
            'can_invite_users', 'can_manage_billing', 'can_export_data',
            'joined_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'joined_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.full_name or obj.user.username
    
    def validate_role(self, value):
        """Validate role assignment based on current user's permissions."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization_membership'):
            current_membership = request.organization_membership
            if current_membership and current_membership.role != 'admin':
                if value == 'admin':
                    raise serializers.ValidationError(
                        "Only admins can assign admin role."
                    )
        return value


class UserInviteSerializer(serializers.Serializer):
    """
    Serializer for inviting users to organization.
    """
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES)
    message = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_email(self, value):
        """Validate email address."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization'):
            organization = request.organization
            
            # Check if user is already a member
            if OrganizationMember.objects.filter(
                organization=organization,
                user__email=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    "User is already a member of this organization."
                )
            
            # Check if there's already a pending invitation
            from organizations.models import OrganizationInvitation
            if OrganizationInvitation.objects.filter(
                organization=organization,
                email=value,
                status='pending'
            ).exists():
                raise serializers.ValidationError(
                    "An invitation has already been sent to this email address."
                )
        
        return value


class UserRoleUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating user roles.
    """
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES)
    can_invite_users = serializers.BooleanField(required=False)
    can_manage_billing = serializers.BooleanField(required=False)
    can_export_data = serializers.BooleanField(required=False)
    
    def validate_role(self, value):
        """Validate role assignment."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization_membership'):
            current_membership = request.organization_membership
            if current_membership and current_membership.role != 'admin':
                if value == 'admin':
                    raise serializers.ValidationError(
                        "Only admins can assign admin role."
                    )
        return value


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activities.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'user_email', 'action', 'description',
            'metadata', 'ip_address', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class UserListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for user lists.
    """
    full_name = serializers.ReadOnlyField()
    role = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'avatar', 'is_verified', 'last_active', 'role', 'is_active'
        ]
        read_only_fields = ['id', 'is_verified', 'last_active']
    
    def get_role(self, obj):
        """Get user's role in current organization."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization'):
            try:
                membership = OrganizationMember.objects.get(
                    user=obj,
                    organization=request.organization,
                    is_active=True
                )
                return membership.role
            except OrganizationMember.DoesNotExist:
                return None
        return None
    
    def get_is_active(self, obj):
        """Get user's active status in current organization."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization'):
            try:
                membership = OrganizationMember.objects.get(
                    user=obj,
                    organization=request.organization,
                    is_active=True
                )
                return membership.is_active
            except OrganizationMember.DoesNotExist:
                return False
        return False

