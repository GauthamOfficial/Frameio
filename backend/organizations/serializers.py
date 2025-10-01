from rest_framework import serializers
from .models import Organization, OrganizationMember, OrganizationInvitation
from users.models import User


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serializer for Organization model.
    """
    members_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website', 'industry',
            'subscription_plan', 'subscription_status', 'ai_generations_used',
            'ai_generations_limit', 'created_at', 'updated_at', 'members_count',
            'is_owner', 'user_role'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ai_generations_used']
    
    def get_members_count(self, obj):
        """Get the number of active members."""
        return obj.members.filter(is_active=True).count()
    
    def get_is_owner(self, obj):
        """Check if current user is the owner."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            return obj.members.filter(
                user=request.user,
                role='owner',
                is_active=True
            ).exists()
        return False
    
    def get_user_role(self, obj):
        """Get current user's role in the organization."""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            membership = obj.members.filter(
                user=request.user,
                is_active=True
            ).first()
            return membership.role if membership else None
        return None


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationMember model.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.SerializerMethodField()
    user_avatar = serializers.CharField(source='user.avatar', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id', 'user', 'user_email', 'user_name', 'user_avatar', 'role',
            'is_active', 'can_invite_users', 'can_manage_billing', 'can_export_data',
            'joined_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'joined_at', 'updated_at']
    
    def get_user_name(self, obj):
        """Get user's full name."""
        return obj.user.full_name or obj.user.username
    
    def validate_role(self, value):
        """Validate role assignment."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization_membership'):
            current_membership = request.organization_membership
            if current_membership and not current_membership.is_admin:
                if value in ['owner', 'admin']:
                    raise serializers.ValidationError(
                        "You don't have permission to assign this role."
                    )
        return value


class OrganizationInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationInvitation model.
    """
    invited_by_name = serializers.CharField(source='invited_by.full_name', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = OrganizationInvitation
        fields = [
            'id', 'email', 'role', 'invited_by', 'invited_by_name', 'organization',
            'organization_name', 'status', 'created_at', 'expires_at', 'is_expired'
        ]
        read_only_fields = ['id', 'invited_by', 'organization', 'created_at', 'expires_at']
    
    def validate_email(self, value):
        """Validate email address."""
        # Check if user is already a member
        organization = self.context.get('organization')
        if organization:
            if OrganizationMember.objects.filter(
                organization=organization,
                user__email=value,
                is_active=True
            ).exists():
                raise serializers.ValidationError(
                    "User is already a member of this organization."
                )
            
            # Check if there's already a pending invitation
            if OrganizationInvitation.objects.filter(
                organization=organization,
                email=value,
                status='pending'
            ).exists():
                raise serializers.ValidationError(
                    "An invitation has already been sent to this email address."
                )
        
        return value


class OrganizationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new organizations.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description', 'website', 'industry']
    
    def create(self, validated_data):
        """Create organization and make creator the owner."""
        request = self.context.get('request')
        organization = Organization.objects.create(**validated_data)
        
        # Create owner membership
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            OrganizationMember.objects.create(
                organization=organization,
                user=request.user,
                role='owner',
                can_invite_users=True,
                can_manage_billing=True,
                can_export_data=True
            )
        
        return organization


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating organization details.
    """
    class Meta:
        model = Organization
        fields = ['name', 'description', 'logo', 'website', 'industry']
    
    def validate(self, attrs):
        """Validate organization update permissions."""
        request = self.context.get('request')
        if request and hasattr(request, 'organization_membership'):
            membership = request.organization_membership
            if not membership or not membership.is_admin:
                raise serializers.ValidationError(
                    "You don't have permission to update this organization."
                )
        return attrs
