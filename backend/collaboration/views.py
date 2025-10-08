from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.core.cache import cache
import logging

from .models import (
    DesignShare, DesignComment, DesignCollaboration, 
    DesignVersion, DesignActivity
)
from .serializers import (
    DesignShareSerializer, DesignShareCreateSerializer,
    DesignCommentSerializer, DesignCommentCreateSerializer,
    DesignCollaborationSerializer, DesignVersionSerializer,
    DesignActivitySerializer, ShareDesignRequestSerializer,
    InviteMemberRequestSerializer, UpdateAccessRequestSerializer,
    CollaborationJoinRequestSerializer, CommentCreateRequestSerializer
)
from .services import CollaborationService
from designs.models import Design
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class DesignShareViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design shares"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DesignShareCreateSerializer
        return DesignShareSerializer
    
    def get_queryset(self):
        """Return shares for current organization"""
        organization = get_current_organization()
        if not organization:
            return DesignShare.objects.none()
        
        queryset = DesignShare.objects.filter(organization=organization)
        
        # Filter by design if provided
        design_id = self.request.query_params.get('design_id')
        if design_id:
            queryset = queryset.filter(design_id=design_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(shared_by=self.request.user) | Q(shared_with=self.request.user)
            )
        
        return queryset.select_related('design', 'shared_by', 'shared_with', 'organization').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new design share"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Create the share
        share = serializer.save(
            organization=organization,
            shared_by=self.request.user
        )
        
        # Generate share token if public
        if share.is_public and not share.share_token:
            import secrets
            share.share_token = secrets.token_urlsafe(32)
            share.save(update_fields=['share_token'])
    
    @action(detail=True, methods=['post'])
    def revoke(self, request, pk=None):
        """Revoke a design share"""
        try:
            share = self.get_object()
            service = CollaborationService()
            service.revoke_share(share, request.user)
            
            return Response(
                {'message': 'Share revoked successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error revoking share {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def update_access(self, request, pk=None):
        """Update access level for a share"""
        try:
            share = self.get_object()
            serializer = UpdateAccessRequestSerializer(data=request.data)
            
            if serializer.is_valid():
                service = CollaborationService()
                updated_share = service.update_access(
                    share=share,
                    updater=request.user,
                    access_level=serializer.validated_data.get('access_level'),
                    allow_download=serializer.validated_data.get('allow_download'),
                    allow_comments=serializer.validated_data.get('allow_comments')
                )
                
                response_serializer = DesignShareSerializer(updated_share)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error updating access for share {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesignCommentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design comments"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return DesignCommentCreateSerializer
        return DesignCommentSerializer
    
    def get_queryset(self):
        """Return comments for current organization"""
        organization = get_current_organization()
        if not organization:
            return DesignComment.objects.none()
        
        queryset = DesignComment.objects.filter(organization=organization)
        
        # Filter by design if provided
        design_id = self.request.query_params.get('design_id')
        if design_id:
            queryset = queryset.filter(design_id=design_id)
        
        # Filter by parent comment if provided
        parent_id = self.request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_comment_id=parent_id)
        else:
            # Only show top-level comments by default
            queryset = queryset.filter(parent_comment__isnull=True)
        
        return queryset.select_related('design', 'author', 'parent_comment', 'organization').order_by('created_at')
    
    def perform_create(self, serializer):
        """Create a new design comment"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Create the comment
        comment = serializer.save(
            organization=organization,
            author=self.request.user
        )
        
        # Create activity record
        service = CollaborationService()
        service._create_activity(
            design=comment.design,
            user=self.request.user,
            activity_type='comment',
            activity_data={'comment_id': str(comment.id)},
            description=f"Added comment on {comment.design.title}",
            related_comment=comment
        )
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark a comment as resolved"""
        try:
            comment = self.get_object()
            
            # Check if user can resolve this comment
            if not (comment.author == request.user or comment.design.can_be_edited_by(request.user)):
                return Response(
                    {'error': 'You don\'t have permission to resolve this comment'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            comment.is_resolved = True
            comment.save(update_fields=['is_resolved'])
            
            return Response(
                {'message': 'Comment resolved successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error resolving comment {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesignCollaborationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing design collaborations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return collaborations for current organization"""
        organization = get_current_organization()
        if not organization:
            return DesignCollaboration.objects.none()
        
        queryset = DesignCollaboration.objects.filter(organization=organization)
        
        # Filter by design if provided
        design_id = self.request.query_params.get('design_id')
        if design_id:
            queryset = queryset.filter(design_id=design_id)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user participation if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(initiator=self.request.user) | Q(participants=self.request.user)
            ).distinct()
        
        return queryset.select_related('design', 'initiator', 'organization').prefetch_related('participants').order_by('-last_activity')
    
    def perform_create(self, serializer):
        """Create a new design collaboration"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Create the collaboration
        collaboration = serializer.save(
            organization=organization,
            initiator=self.request.user
        )
        
        # Add initiator as participant
        collaboration.add_participant(self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join a collaboration session"""
        try:
            collaboration = self.get_object()
            service = CollaborationService()
            service.join_collaboration(collaboration, request.user)
            
            return Response(
                {'message': 'Joined collaboration successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error joining collaboration {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """Leave a collaboration session"""
        try:
            collaboration = self.get_object()
            collaboration.remove_participant(request.user)
            
            return Response(
                {'message': 'Left collaboration successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error leaving collaboration {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def end(self, request, pk=None):
        """End a collaboration session"""
        try:
            collaboration = self.get_object()
            service = CollaborationService()
            service.end_collaboration(collaboration, request.user)
            
            return Response(
                {'message': 'Collaboration ended successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error ending collaboration {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesignVersionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing design versions"""
    
    serializer_class = DesignVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return versions for current organization"""
        organization = get_current_organization()
        if not organization:
            return DesignVersion.objects.none()
        
        queryset = DesignVersion.objects.filter(organization=organization)
        
        # Filter by design if provided
        design_id = self.request.query_params.get('design_id')
        if design_id:
            queryset = queryset.filter(design_id=design_id)
        
        return queryset.select_related('design', 'created_by', 'collaboration', 'organization').order_by('-version_number')
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a design version"""
        try:
            version = self.get_object()
            
            # Check if user has permission to restore this version
            if not version.design.can_be_edited_by(request.user):
                return Response(
                    {'error': 'You don\'t have permission to restore this version'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Restore the version
            version.restore()
            
            return Response(
                {'message': 'Version restored successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error restoring version {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DesignActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing design activities"""
    
    serializer_class = DesignActivitySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return activities for current organization"""
        organization = get_current_organization()
        if not organization:
            return DesignActivity.objects.none()
        
        queryset = DesignActivity.objects.filter(organization=organization)
        
        # Filter by design if provided
        design_id = self.request.query_params.get('design_id')
        if design_id:
            queryset = queryset.filter(design_id=design_id)
        
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by activity type if provided
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        return queryset.select_related('design', 'user', 'related_comment', 'related_collaboration', 'related_version', 'organization').order_by('-created_at')


class CollaborationAPIView(viewsets.ViewSet):
    """Main API view for collaboration features"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = CollaborationService()
    
    @action(detail=False, methods=['post'])
    def share_design(self, request):
        """Share a design with a user or publicly"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = ShareDesignRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the design
            design = Design.objects.get(
                id=serializer.validated_data['design_id'],
                organization=organization
            )
            
            # Share the design
            share = self.service.share_design(
                design=design,
                shared_by=request.user,
                shared_with_email=serializer.validated_data.get('shared_with_email'),
                access_level=serializer.validated_data.get('access_level', 'view'),
                is_public=serializer.validated_data.get('is_public', False),
                allow_download=serializer.validated_data.get('allow_download', False),
                allow_comments=serializer.validated_data.get('allow_comments', True),
                expires_at=serializer.validated_data.get('expires_at'),
                message=serializer.validated_data.get('message', '')
            )
            
            response_serializer = DesignShareSerializer(share)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Design.DoesNotExist:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Design sharing failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def invite_member(self, request):
        """Invite a member to collaborate on a design"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = InviteMemberRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the design
            design_id = request.data.get('design_id')
            if not design_id:
                return Response(
                    {"error": "design_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            design = Design.objects.get(
                id=design_id,
                organization=organization
            )
            
            # Invite the member
            share = self.service.invite_member(
                design=design,
                inviter=request.user,
                email=serializer.validated_data['email'],
                access_level=serializer.validated_data.get('access_level', 'view'),
                message=serializer.validated_data.get('message', '')
            )
            
            response_serializer = DesignShareSerializer(share)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Design.DoesNotExist:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Member invitation failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def add_comment(self, request):
        """Add a comment to a design"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = CommentCreateRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the design
            design = Design.objects.get(
                id=serializer.validated_data['design_id'],
                organization=organization
            )
            
            # Get parent comment if provided
            parent_comment = None
            if serializer.validated_data.get('parent_comment_id'):
                parent_comment = DesignComment.objects.get(
                    id=serializer.validated_data['parent_comment_id'],
                    organization=organization
                )
            
            # Add the comment
            comment = self.service.add_comment(
                design=design,
                author=request.user,
                content=serializer.validated_data['content'],
                parent_comment=parent_comment
            )
            
            response_serializer = DesignCommentSerializer(comment, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Design.DoesNotExist:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except DesignComment.DoesNotExist:
            return Response(
                {"error": "Parent comment not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Comment creation failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def start_collaboration(self, request):
        """Start a collaboration session on a design"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the design
            design_id = request.data.get('design_id')
            if not design_id:
                return Response(
                    {"error": "design_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            design = Design.objects.get(
                id=design_id,
                organization=organization
            )
            
            # Start collaboration
            collaboration = self.service.start_collaboration(
                design=design,
                initiator=request.user,
                allow_edit=request.data.get('allow_edit', True),
                allow_comments=request.data.get('allow_comments', True),
                auto_save=request.data.get('auto_save', True)
            )
            
            response_serializer = DesignCollaborationSerializer(collaboration, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            
        except Design.DoesNotExist:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Collaboration start failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def join_collaboration(self, request):
        """Join an existing collaboration session"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = CollaborationJoinRequestSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get the collaboration
            collaboration = DesignCollaboration.objects.get(
                id=serializer.validated_data['collaboration_id'],
                organization=organization
            )
            
            # Join the collaboration
            self.service.join_collaboration(collaboration, request.user)
            
            response_serializer = DesignCollaborationSerializer(collaboration, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_200_OK)
            
        except DesignCollaboration.DoesNotExist:
            return Response(
                {"error": "Collaboration not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Collaboration join failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """Get design activity"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            design_id = request.query_params.get('design_id')
            user_id = request.query_params.get('user_id')
            limit = int(request.query_params.get('limit', 50))
            
            if design_id:
                design = Design.objects.get(id=design_id, organization=organization)
                activities = self.service.get_design_activity(design, limit)
            elif user_id:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                user = User.objects.get(id=user_id)
                activities = self.service.get_user_activity(user, limit)
            else:
                return Response(
                    {"error": "design_id or user_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer = DesignActivitySerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Design.DoesNotExist:
            return Response(
                {"error": "Design not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Activity retrieval failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )