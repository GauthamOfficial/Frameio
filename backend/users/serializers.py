"""
User serializers for the Framio application.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserProfile, CompanyProfile

User = get_user_model()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer that allows login with email instead of username.
    """
    username_field = 'email'

    def validate(self, attrs):
        """
        Validate and authenticate user using email instead of username.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Get email from request data
        email = attrs.get('email', '')
        if email:
            email = email.strip()
        password = attrs.get('password', '')
        
        logger.info(f"Login attempt - Email: '{email}', Password provided: {bool(password)}, Attrs keys: {list(attrs.keys())}")
        
        if not email:
            raise serializers.ValidationError({'email': 'Email is required.'})
        
        if not password:
            raise serializers.ValidationError({'password': 'Password is required.'})
        
        # Try to get user by email (case-insensitive lookup)
        try:
            # Use case-insensitive email lookup
            user = User.objects.get(email__iexact=email)
            logger.info(f"User found: {user.username} (email: {user.email}, active: {user.is_active})")
        except User.DoesNotExist:
            logger.warning(f"User not found for email: {email}")
            # Don't reveal if email exists or not for security
            raise serializers.ValidationError({'non_field_errors': ['No active account found with the given credentials.']})
        except User.MultipleObjectsReturned:
            # If multiple users with same email (shouldn't happen, but handle it)
            logger.warning(f"Multiple users found for email: {email}")
            user = User.objects.filter(email__iexact=email).first()
        
        # Verify password
        password_valid = user.check_password(password)
        logger.info(f"Password check for user {user.username}: {password_valid}")
        if not password_valid:
            logger.warning(f"Invalid password for user: {user.email}")
            # Don't reveal if password is wrong or user doesn't exist
            raise serializers.ValidationError({'non_field_errors': ['No active account found with the given credentials.']})
        
        # Check if user is active
        if not user.is_active:
            logger.warning(f"User account is disabled: {user.email}")
            raise serializers.ValidationError({'non_field_errors': ['User account is disabled.']})
        
        # Generate tokens directly using RefreshToken
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        logger.info("Tokens generated successfully")
        
        # Add user to serializer for access in view
        self.user = user
        
        # Return tokens in the format expected by the view
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'avatar', 'phone_number', 'bio', 'location', 'website',
            'timezone', 'language', 'theme', 'is_verified', 'last_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'created_at', 'updated_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating User model."""
    
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'avatar', 'phone_number',
            'bio', 'location', 'website', 'timezone', 'language', 'theme'
        ]


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing users."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active']


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating UserProfile model."""
    
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['user']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """Serializer for OrganizationMember model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class UserInviteSerializer(serializers.Serializer):
    """Serializer for inviting users."""
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=['admin', 'manager', 'designer'])


class UserRoleUpdateSerializer(serializers.Serializer):
    """Serializer for updating user roles."""
    role = serializers.ChoiceField(choices=['admin', 'manager', 'designer'])
    can_invite_users = serializers.BooleanField(required=False)
    can_manage_billing = serializers.BooleanField(required=False)
    can_export_data = serializers.BooleanField(required=False)


class UserActivitySerializer(serializers.ModelSerializer):
    """Serializer for UserActivity model."""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'


class CompanyProfileSerializer(serializers.ModelSerializer):
    """Serializer for CompanyProfile model."""
    logo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def get_logo_url(self, obj):
        if obj.logo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.logo.url)
            return obj.logo.url
        return None


class CompanyProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating CompanyProfile model."""
    
    class Meta:
        model = CompanyProfile
        fields = '__all__'
        read_only_fields = ['user', 'created_at', 'updated_at']
