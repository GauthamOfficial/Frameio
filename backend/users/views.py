"""
User management views with tenant scoping and role-based permissions.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import uuid
import logging

from .models import User, UserProfile, UserActivity, CompanyProfile
from .serializers import (
    UserSerializer, UserUpdateSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, OrganizationMemberSerializer,
    UserInviteSerializer, UserRoleUpdateSerializer, UserActivitySerializer,
    UserListSerializer, CompanyProfileSerializer, CompanyProfileUpdateSerializer
)
from .permissions import (
    IsOrganizationMember, IsOrganizationAdmin, IsOrganizationManager,
    CanManageUsers, get_user_organization_permissions, IsAdminRequest,
    IsAuthenticatedOrAdmin, IsOrganizationMemberOrAdmin, CanManageUsersOrAdmin
)
from organizations.models import OrganizationMember, OrganizationInvitation

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users within an organization.
    Supports both normal authenticated requests and admin panel requests.
    """
    queryset = User.objects.all()
    permission_classes = [IsAuthenticatedOrAdmin, IsOrganizationMemberOrAdmin, CanManageUsersOrAdmin]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def get_queryset(self):
        """Filter users based on current organization, or return all users for admin requests."""
        # If this is an admin request, return all users
        if getattr(self.request, '_admin_request', False):
            return User.objects.all()
        
        # Otherwise, filter by organization
        organization = getattr(self.request, 'organization', None)
        if organization:
            # Return users who are members of the current organization
            return User.objects.filter(
                organization_memberships__organization=organization,
                organization_memberships__is_active=True
            ).distinct()
        return User.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """Get user details."""
        user = self.get_object()
        
        # Admin requests can access any user
        if getattr(request, '_admin_request', False):
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        
        # Check if user is in the same organization
        organization = getattr(request, 'organization', None)
        if organization:
            if not OrganizationMember.objects.filter(
                user=user,
                organization=organization,
                is_active=True
            ).exists():
                return Response(
                    {'error': 'User not found in this organization'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        serializer = self.get_serializer(user)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        user = self.get_object()
        
        # Admin requests can update any user
        if not getattr(request, '_admin_request', False):
            # Users can only update their own profile unless they're admin
            if user != request.user:
                membership = getattr(request, 'organization_membership', None)
                if not membership or membership.role != 'admin':
                    return Response(
                        {'error': 'Permission denied'},
                        status=status.HTTP_403_FORBIDDEN
                    )
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete user."""
        user = self.get_object()
        
        logger.info(f"Delete request for user {user.id} ({user.email})")
        logger.info(f"Is admin request: {getattr(request, '_admin_request', False)}")
        
        # Admin requests can delete any user
        if not getattr(request, '_admin_request', False):
            # Regular users cannot delete users (only admins)
            membership = getattr(request, 'organization_membership', None)
            if not membership or membership.role != 'admin':
                logger.warning(f"Delete denied: insufficient permissions")
                return Response(
                    {'error': 'Permission denied - Admin access required'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        try:
            user_email = user.email
            user.delete()
            logger.info(f"User {user_email} deleted successfully")
            return Response(
                {'message': f'User {user_email} deleted successfully'},
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return Response(
                {'error': f'Failed to delete user: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_role(self, request, pk=None):
        """Update user's role in the organization."""
        user = self.get_object()
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'No organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is in the organization
        try:
            membership = OrganizationMember.objects.get(
                user=user,
                organization=organization,
                is_active=True
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'User not found in this organization'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = UserRoleUpdateSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Update role and permissions
            membership.role = serializer.validated_data['role']
            
            # Update permissions based on role
            if membership.role == 'admin':
                membership.can_invite_users = True
                membership.can_manage_billing = True
                membership.can_export_data = True
            elif membership.role == 'manager':
                membership.can_invite_users = True
                membership.can_manage_billing = False
                membership.can_export_data = True
            else:  # designer
                membership.can_invite_users = False
                membership.can_manage_billing = False
                membership.can_export_data = False
            
            # Override with explicit permissions if provided
            if 'can_invite_users' in serializer.validated_data:
                membership.can_invite_users = serializer.validated_data['can_invite_users']
            if 'can_manage_billing' in serializer.validated_data:
                membership.can_manage_billing = serializer.validated_data['can_manage_billing']
            if 'can_export_data' in serializer.validated_data:
                membership.can_export_data = serializer.validated_data['can_export_data']
            
            membership.save()
            
            logger.info(
                f"User {user.email} role updated to {membership.role} "
                f"in organization {organization.name} by {request.user.email}"
            )
            
            return Response({
                'message': 'User role updated successfully',
                'role': membership.role,
                'permissions': {
                    'can_invite_users': membership.can_invite_users,
                    'can_manage_billing': membership.can_manage_billing,
                    'can_export_data': membership.can_export_data,
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def remove_from_organization(self, request, pk=None):
        """Remove user from the organization."""
        user = self.get_object()
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'No organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if user is in the organization
        try:
            membership = OrganizationMember.objects.get(
                user=user,
                organization=organization,
                is_active=True
            )
        except OrganizationMember.DoesNotExist:
            return Response(
                {'error': 'User not found in this organization'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Don't allow removing the last admin
        if membership.role == 'admin':
            admin_count = OrganizationMember.objects.filter(
                organization=organization,
                role='admin',
                is_active=True
            ).count()
            
            if admin_count <= 1:
                return Response(
                    {'error': 'Cannot remove the last admin from the organization'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Deactivate membership
        membership.is_active = False
        membership.save()
        
        logger.info(
            f"User {user.email} removed from organization {organization.name} "
            f"by {request.user.email}"
        )
        
        return Response({'message': 'User removed from organization successfully'})
    
    @action(detail=False, methods=['post'])
    def invite_user(self, request):
        """Invite a new user to the organization."""
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'No organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserInviteSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            # Create invitation
            invitation = OrganizationInvitation.objects.create(
                organization=organization,
                email=serializer.validated_data['email'],
                role=serializer.validated_data['role'],
                invited_by=request.user,
                token=str(uuid.uuid4()),
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # TODO: Send invitation email
            
            logger.info(
                f"Invitation sent to {invitation.email} for organization "
                f"{organization.name} by {request.user.email}"
            )
            
            return Response({
                'message': 'Invitation sent successfully',
                'invitation_id': str(invitation.id),
                'expires_at': invitation.expires_at
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def invitations(self, request):
        """Get pending invitations for the organization."""
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'No organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        invitations = OrganizationInvitation.objects.filter(
            organization=organization,
            status='pending'
        ).order_by('-created_at')
        
        invitation_data = []
        for invitation in invitations:
            invitation_data.append({
                'id': str(invitation.id),
                'email': invitation.email,
                'role': invitation.role,
                'invited_by': invitation.invited_by.email,
                'created_at': invitation.created_at,
                'expires_at': invitation.expires_at,
                'is_expired': invitation.is_expired
            })
        
        return Response(invitation_data)
    
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """Get current user's permissions in the organization."""
        organization = getattr(request, 'organization', None)
        
        if not organization:
            return Response(
                {'error': 'No organization context'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        permissions = get_user_organization_permissions(request.user, organization)
        
        if not permissions:
            return Response(
                {'error': 'User not found in this organization'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response(permissions)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles.
    """
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer
    
    def get_queryset(self):
        """Filter profiles based on current organization."""
        organization = getattr(self.request, 'organization', None)
        if organization:
            return UserProfile.objects.filter(
                user__organization_memberships__organization=organization,
                user__organization_memberships__is_active=True
            ).distinct()
        return UserProfile.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """Get user profile."""
        profile = self.get_object()
        
        # Users can only view their own profile unless they're admin
        if profile.user != request.user:
            membership = getattr(request, 'organization_membership', None)
            if not membership or membership.role != 'admin':
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        profile = self.get_object()
        
        # Users can only update their own profile unless they're admin
        if profile.user != request.user:
            membership = getattr(request, 'organization_membership', None)
            if not membership or membership.role != 'admin':
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing user activities (read-only).
    """
    queryset = UserActivity.objects.all()
    serializer_class = UserActivitySerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """Filter activities based on current organization."""
        organization = getattr(self.request, 'organization', None)
        if organization:
            return UserActivity.objects.filter(
                user__organization_memberships__organization=organization,
                user__organization_memberships__is_active=True
            ).distinct()
        return UserActivity.objects.none()


class CompanyProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing company profiles.
    """
    queryset = CompanyProfile.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action in ['update', 'partial_update']:
            return CompanyProfileUpdateSerializer
        return CompanyProfileSerializer
    
    def get_queryset(self):
        """Filter company profiles based on current user."""
        return CompanyProfile.objects.filter(user=self.request.user)
    
    def get_object(self):
        """Get or create company profile for current user."""
        # For list view, return the user's profile
        if self.action == 'list':
            profile, created = CompanyProfile.objects.get_or_create(
                user=self.request.user
            )
            return profile
        
        # For detail view, get the profile by pk or create if it doesn't exist
        try:
            profile = CompanyProfile.objects.get(
                user=self.request.user,
                pk=self.kwargs.get('pk')
            )
        except CompanyProfile.DoesNotExist:
            profile, created = CompanyProfile.objects.get_or_create(
                user=self.request.user
            )
        return profile
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def list(self, request, *args, **kwargs):
        """Get current user's company profile."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create or update company profile for current user.
        Accepts JSON, form-encoded, and multipart (for logo uploads).
        """
        try:
            profile, created = CompanyProfile.objects.get_or_create(
                user=request.user
            )
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self, request, *args, **kwargs):
        """Get current user's company profile."""
        profile = self.get_object()
        serializer = self.get_serializer(profile)
        return Response(serializer.data)
    
    
    def update(self, request, *args, **kwargs):
        """Update current user's company profile. Supports multipart uploads."""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def partial_update(self, request, *args, **kwargs):
        """Partially update current user's company profile."""
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """Delete current user's company profile."""
        profile = self.get_object()
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get company profile completion status."""
        profile = self.get_object()
        return Response({
            'has_profile': bool(profile.company_name),
            'has_logo': bool(profile.logo),
            'has_contact_info': bool(
                profile.whatsapp_number or profile.email
            ),
            'is_complete': profile.has_complete_profile,
            'completion_percentage': self._calculate_completion_percentage(profile)
        })
    
    def _calculate_completion_percentage(self, profile):
        """Calculate profile completion percentage."""
        fields = [
            'company_name', 'logo', 'whatsapp_number', 'email', 
            'website', 'address', 'description'
        ]
        completed = sum(1 for field in fields if getattr(profile, field))
        return int((completed / len(fields)) * 100)
