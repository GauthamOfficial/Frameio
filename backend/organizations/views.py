from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
import uuid
import logging

from .models import Organization, OrganizationMember, OrganizationInvitation
from .serializers import (
    OrganizationSerializer, OrganizationMemberSerializer,
    OrganizationInvitationSerializer, OrganizationCreateSerializer,
    OrganizationUpdateSerializer
)
from users.models import User
from users.permissions import (
    IsOrganizationMember, IsOrganizationAdmin, IsOrganizationManager,
    CanManageUsers, CanManageBilling
)

logger = logging.getLogger(__name__)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organizations.
    """
    queryset = Organization.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return OrganizationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return OrganizationUpdateSerializer
        return OrganizationSerializer
    
    def get_queryset(self):
        """Filter organizations based on user membership."""
        if self.action == 'list':
            # Return organizations where user is a member
            return Organization.objects.filter(
                members__user=self.request.user,
                members__is_active=True
            ).distinct()
        elif self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            # For detail views, check if user is a member
            org_id = self.kwargs.get('pk')
            if org_id:
                try:
                    org = Organization.objects.get(id=org_id)
                    if OrganizationMember.objects.filter(
                        organization=org,
                        user=self.request.user,
                        is_active=True
                    ).exists():
                        return Organization.objects.filter(id=org_id)
                except Organization.DoesNotExist:
                    pass
            return Organization.objects.none()
        return super().get_queryset()
    
    def perform_create(self, serializer):
        """Create organization and set creator as owner."""
        with transaction.atomic():
            organization = serializer.save()
            
            # Create owner membership
            OrganizationMember.objects.create(
                organization=organization,
                user=self.request.user,
                role='owner',
                can_invite_users=True,
                can_manage_billing=True,
                can_export_data=True
            )
            
            logger.info(f"Organization {organization.name} created by {self.request.user.email}")
    
    def perform_update(self, serializer):
        """Update organization with permission check."""
        # Check if user has permission to update
        membership = getattr(self.request, 'organization_membership', None)
        if not membership or not membership.is_admin:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
        logger.info(f"Organization {serializer.instance.name} updated by {self.request.user.email}")
    
    def perform_destroy(self, instance):
        """Delete organization (only by owner)."""
        membership = getattr(self.request, 'organization_membership', None)
        if not membership or membership.role != 'owner':
            return Response(
                {'error': 'Only organization owners can delete organizations'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        logger.info(f"Organization {instance.name} deleted by {self.request.user.email}")
        instance.delete()
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get organization members."""
        organization = self.get_object()
        
        # Check if user has access to organization
        if not self.user_has_organization_access(organization):
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        members = organization.members.filter(is_active=True)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def invite_member(self, request, pk=None):
        """Invite a new member to the organization."""
        organization = self.get_object()
        
        # Check if user has permission to invite
        membership = getattr(request, 'organization_membership', None)
        if not membership or not membership.can_invite_users:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrganizationInvitationSerializer(
            data=request.data,
            context={'organization': organization, 'request': request}
        )
        
        if serializer.is_valid():
            # Create invitation
            invitation = serializer.save(
                organization=organization,
                invited_by=request.user,
                token=str(uuid.uuid4()),
                expires_at=timezone.now() + timedelta(days=7)
            )
            
            # TODO: Send invitation email
            
            logger.info(f"Invitation sent to {invitation.email} for organization {organization.name}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def invitations(self, request, pk=None):
        """Get organization invitations."""
        organization = self.get_object()
        
        # Check if user has access to organization
        if not self.user_has_organization_access(organization):
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        invitations = organization.invitations.all()
        serializer = OrganizationInvitationSerializer(invitations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get organization usage statistics."""
        organization = self.get_object()
        
        # Check if user has access to organization
        if not self.user_has_organization_access(organization):
            return Response(
                {'error': 'Access denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        usage_data = {
            'ai_generations_used': organization.ai_generations_used,
            'ai_generations_limit': organization.ai_generations_limit,
            'usage_percentage': (organization.ai_generations_used / organization.ai_generations_limit) * 100,
            'subscription_plan': organization.subscription_plan,
            'subscription_status': organization.subscription_status,
        }
        
        return Response(usage_data)
    
    def user_has_organization_access(self, organization):
        """Check if user has access to organization."""
        return OrganizationMember.objects.filter(
            organization=organization,
            user=self.request.user,
            is_active=True
        ).exists()


class OrganizationMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization members.
    """
    queryset = OrganizationMember.objects.all()
    serializer_class = OrganizationMemberSerializer
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMember]
    
    def get_queryset(self):
        """Filter members based on current organization."""
        # Get organization from URL or request context
        org_id = self.kwargs.get('organization_pk')
        if org_id:
            try:
                organization = Organization.objects.get(id=org_id)
                # Check if user is a member of this organization
                if OrganizationMember.objects.filter(
                    organization=organization,
                    user=self.request.user,
                    is_active=True
                ).exists():
                    return OrganizationMember.objects.filter(
                        organization=organization,
                        is_active=True
                    )
            except Organization.DoesNotExist:
                pass
        
        # Fallback to request organization context
        organization = getattr(self.request, 'organization', None)
        if organization:
            return OrganizationMember.objects.filter(
                organization=organization,
                is_active=True
            )
        return OrganizationMember.objects.none()
    
    def perform_update(self, serializer):
        """Update member with permission check."""
        # Check if user has permission to manage members
        membership = getattr(self.request, 'organization_membership', None)
        if not membership or not membership.can_invite_users:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Remove member from organization."""
        # Check if user has permission to manage members
        membership = getattr(self.request, 'organization_membership', None)
        if not membership or not membership.can_invite_users:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Don't allow removing the last owner
        if instance.role == 'owner':
            owner_count = OrganizationMember.objects.filter(
                organization=instance.organization,
                role='owner',
                is_active=True
            ).count()
            
            if owner_count <= 1:
                return Response(
                    {'error': 'Cannot remove the last owner'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        instance.is_active = False
        instance.save()
        
        logger.info(f"Member {instance.user.email} removed from organization {instance.organization.name}")


class OrganizationInvitationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing organization invitations.
    """
    queryset = OrganizationInvitation.objects.all()
    serializer_class = OrganizationInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageUsers]
    
    def get_queryset(self):
        """Filter invitations based on current organization."""
        # Get organization from URL or request context
        org_id = self.kwargs.get('organization_pk')
        if org_id:
            try:
                organization = Organization.objects.get(id=org_id)
                # Check if user is a member of this organization
                if OrganizationMember.objects.filter(
                    organization=organization,
                    user=self.request.user,
                    is_active=True
                ).exists():
                    return OrganizationInvitation.objects.filter(organization=organization)
            except Organization.DoesNotExist:
                pass
        
        # Fallback to request organization context
        organization = getattr(self.request, 'organization', None)
        if organization:
            return OrganizationInvitation.objects.filter(organization=organization)
        return OrganizationInvitation.objects.none()
    
    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept an invitation."""
        invitation = self.get_object()
        
        # Check if invitation is valid
        if invitation.is_expired or invitation.status != 'pending':
            return Response(
                {'error': 'Invalid or expired invitation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Accept invitation
        if invitation.accept(request.user):
            return Response({'message': 'Invitation accepted successfully'})
        else:
            return Response(
                {'error': 'Failed to accept invitation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def decline(self, request, pk=None):
        """Decline an invitation."""
        invitation = self.get_object()
        
        if invitation.decline():
            return Response({'message': 'Invitation declined'})
        else:
            return Response(
                {'error': 'Failed to decline invitation'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_destroy(self, instance):
        """Cancel an invitation."""
        # Check if user has permission to manage invitations
        membership = getattr(self.request, 'organization_membership', None)
        if not membership or not membership.can_invite_users:
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance.delete()
        logger.info(f"Invitation to {instance.email} cancelled")