import secrets
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from typing import Dict, List, Optional, Any
import uuid

from .models import (
    DesignShare, DesignComment, DesignCollaboration, 
    DesignVersion, DesignActivity
)
from designs.models import Design
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class CollaborationService:
    """Service for managing design collaboration features"""
    
    def __init__(self):
        self.base_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    def share_design(
        self,
        design: Design,
        shared_by,
        shared_with_email: str = None,
        access_level: str = 'view',
        is_public: bool = False,
        allow_download: bool = False,
        allow_comments: bool = True,
        expires_at: timezone.datetime = None,
        message: str = ""
    ) -> DesignShare:
        """
        Share a design with a user or publicly
        
        Args:
            design: Design to share
            shared_by: User sharing the design
            shared_with_email: Email of user to share with (for private shares)
            access_level: Access level (view, comment, edit, admin)
            is_public: Whether to share publicly
            allow_download: Whether to allow downloads
            allow_comments: Whether to allow comments
            expires_at: When the share expires
            message: Optional message
            
        Returns:
            Created DesignShare instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Check if user has permission to share this design
        if not design.can_be_edited_by(shared_by):
            raise ValueError("You don't have permission to share this design")
        
        # Get shared_with user if email provided
        shared_with = None
        if shared_with_email and not is_public:
            try:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                shared_with = User.objects.get(email=shared_with_email)
            except User.DoesNotExist:
                # User doesn't exist, we'll create a share but send invitation email
                pass
        
        # Generate share token for public shares
        share_token = None
        if is_public:
            share_token = secrets.token_urlsafe(32)
        
        # Create the share
        share = DesignShare.objects.create(
            organization=organization,
            design=design,
            shared_by=shared_by,
            shared_with=shared_with,
            access_level=access_level,
            is_public=is_public,
            allow_download=allow_download,
            allow_comments=allow_comments,
            expires_at=expires_at,
            message=message,
            share_token=share_token
        )
        
        # Create activity record
        self._create_activity(
            design=design,
            user=shared_by,
            activity_type='share',
            activity_data={
                'share_id': str(share.id),
                'access_level': access_level,
                'is_public': is_public,
                'shared_with_email': shared_with_email
            },
            description=f"Shared design with {shared_with_email if shared_with_email else 'public'}"
        )
        
        # Send notification email if sharing with specific user
        if shared_with_email and not is_public:
            self._send_share_notification(share, shared_with_email)
        
        logger.info(f"Design {design.id} shared by {shared_by.id}")
        return share
    
    def invite_member(
        self,
        design: Design,
        inviter,
        email: str,
        access_level: str = 'view',
        message: str = ""
    ) -> DesignShare:
        """
        Invite a member to collaborate on a design
        
        Args:
            design: Design to invite to
            inviter: User sending the invitation
            email: Email of user to invite
            access_level: Access level for the invitation
            message: Optional invitation message
            
        Returns:
            Created DesignShare instance
        """
        return self.share_design(
            design=design,
            shared_by=inviter,
            shared_with_email=email,
            access_level=access_level,
            is_public=False,
            allow_download=True,
            allow_comments=True,
            message=message
        )
    
    def update_access(
        self,
        share: DesignShare,
        updater,
        access_level: str = None,
        allow_download: bool = None,
        allow_comments: bool = None
    ) -> DesignShare:
        """
        Update access level for a design share
        
        Args:
            share: DesignShare to update
            updater: User updating the access
            access_level: New access level
            allow_download: New download permission
            allow_comments: New comments permission
            
        Returns:
            Updated DesignShare instance
        """
        # Check if user has permission to update this share
        if not share.design.can_be_edited_by(updater):
            raise ValueError("You don't have permission to update this share")
        
        # Update fields
        if access_level is not None:
            share.access_level = access_level
        if allow_download is not None:
            share.allow_download = allow_download
        if allow_comments is not None:
            share.allow_comments = allow_comments
        
        share.save()
        
        # Create activity record
        self._create_activity(
            design=share.design,
            user=updater,
            activity_type='share',
            activity_data={
                'share_id': str(share.id),
                'action': 'updated',
                'access_level': share.access_level,
                'allow_download': share.allow_download,
                'allow_comments': share.allow_comments
            },
            description=f"Updated access for {share.shared_with.get_full_name() if share.shared_with else 'public share'}"
        )
        
        logger.info(f"Access updated for share {share.id} by {updater.id}")
        return share
    
    def revoke_share(self, share: DesignShare, revoker) -> bool:
        """
        Revoke a design share
        
        Args:
            share: DesignShare to revoke
            revoker: User revoking the share
            
        Returns:
            True if successful
        """
        # Check if user has permission to revoke this share
        if not share.design.can_be_edited_by(revoker):
            raise ValueError("You don't have permission to revoke this share")
        
        # Revoke the share
        share.revoke()
        
        # Create activity record
        self._create_activity(
            design=share.design,
            user=revoker,
            activity_type='share',
            activity_data={
                'share_id': str(share.id),
                'action': 'revoked'
            },
            description=f"Revoked access for {share.shared_with.get_full_name() if share.shared_with else 'public share'}"
        )
        
        logger.info(f"Share {share.id} revoked by {revoker.id}")
        return True
    
    def add_comment(
        self,
        design: Design,
        author,
        content: str,
        parent_comment: DesignComment = None
    ) -> DesignComment:
        """
        Add a comment to a design
        
        Args:
            design: Design to comment on
            author: User adding the comment
            content: Comment content
            parent_comment: Parent comment if this is a reply
            
        Returns:
            Created DesignComment instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Check if user has permission to comment
        if not self._can_comment(design, author):
            raise ValueError("You don't have permission to comment on this design")
        
        # Create the comment
        comment = DesignComment.objects.create(
            organization=organization,
            design=design,
            author=author,
            parent_comment=parent_comment,
            content=content
        )
        
        # Create activity record
        self._create_activity(
            design=design,
            user=author,
            activity_type='comment',
            activity_data={
                'comment_id': str(comment.id),
                'parent_comment_id': str(parent_comment.id) if parent_comment else None
            },
            description=f"Added comment on {design.title}",
            related_comment=comment
        )
        
        logger.info(f"Comment added to design {design.id} by {author.id}")
        return comment
    
    def start_collaboration(
        self,
        design: Design,
        initiator,
        allow_edit: bool = True,
        allow_comments: bool = True,
        auto_save: bool = True
    ) -> DesignCollaboration:
        """
        Start a collaboration session on a design
        
        Args:
            design: Design to collaborate on
            initiator: User starting the collaboration
            allow_edit: Whether to allow editing
            allow_comments: Whether to allow comments
            auto_save: Whether to auto-save changes
            
        Returns:
            Created DesignCollaboration instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Check if user has permission to start collaboration
        if not design.can_be_edited_by(initiator):
            raise ValueError("You don't have permission to start collaboration on this design")
        
        # Check if there's already an active collaboration
        existing_collaboration = DesignCollaboration.objects.filter(
            design=design,
            status='active',
            organization=organization
        ).first()
        
        if existing_collaboration:
            # Add initiator to existing collaboration
            existing_collaboration.add_participant(initiator)
            return existing_collaboration
        
        # Create new collaboration
        collaboration = DesignCollaboration.objects.create(
            organization=organization,
            design=design,
            initiator=initiator,
            allow_edit=allow_edit,
            allow_comments=allow_comments,
            auto_save=auto_save
        )
        
        # Add initiator as participant
        collaboration.add_participant(initiator)
        
        # Create activity record
        self._create_activity(
            design=design,
            user=initiator,
            activity_type='collaboration_start',
            activity_data={
                'collaboration_id': str(collaboration.id)
            },
            description=f"Started collaboration on {design.title}",
            related_collaboration=collaboration
        )
        
        logger.info(f"Collaboration started on design {design.id} by {initiator.id}")
        return collaboration
    
    def join_collaboration(
        self,
        collaboration: DesignCollaboration,
        user
    ) -> bool:
        """
        Join an existing collaboration session
        
        Args:
            collaboration: Collaboration to join
            user: User joining the collaboration
            
        Returns:
            True if successful
        """
        # Check if user can join this collaboration
        if not collaboration.can_join(user):
            raise ValueError("You don't have permission to join this collaboration")
        
        # Add user to collaboration
        collaboration.add_participant(user)
        
        # Create activity record
        self._create_activity(
            design=collaboration.design,
            user=user,
            activity_type='collaboration_start',
            activity_data={
                'collaboration_id': str(collaboration.id),
                'action': 'joined'
            },
            description=f"Joined collaboration on {collaboration.design.title}",
            related_collaboration=collaboration
        )
        
        logger.info(f"User {user.id} joined collaboration {collaboration.id}")
        return True
    
    def end_collaboration(
        self,
        collaboration: DesignCollaboration,
        user
    ) -> bool:
        """
        End a collaboration session
        
        Args:
            collaboration: Collaboration to end
            user: User ending the collaboration
            
        Returns:
            True if successful
        """
        # Check if user has permission to end this collaboration
        if not (collaboration.initiator == user or collaboration.design.can_be_edited_by(user)):
            raise ValueError("You don't have permission to end this collaboration")
        
        # End the collaboration
        collaboration.end_collaboration()
        
        # Create activity record
        self._create_activity(
            design=collaboration.design,
            user=user,
            activity_type='collaboration_end',
            activity_data={
                'collaboration_id': str(collaboration.id)
            },
            description=f"Ended collaboration on {collaboration.design.title}",
            related_collaboration=collaboration
        )
        
        logger.info(f"Collaboration {collaboration.id} ended by {user.id}")
        return True
    
    def create_version(
        self,
        design: Design,
        user,
        changes_summary: str = "",
        collaboration: DesignCollaboration = None
    ) -> DesignVersion:
        """
        Create a new version of a design
        
        Args:
            design: Design to create version for
            user: User creating the version
            changes_summary: Summary of changes made
            collaboration: Related collaboration session
            
        Returns:
            Created DesignVersion instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Get next version number
        last_version = DesignVersion.objects.filter(
            design=design,
            organization=organization
        ).order_by('-version_number').first()
        
        version_number = (last_version.version_number + 1) if last_version else 1
        
        # Create the version
        version = DesignVersion.objects.create(
            organization=organization,
            design=design,
            version_number=version_number,
            created_by=user,
            collaboration=collaboration,
            version_data=design.metadata,
            changes_summary=changes_summary,
            image=design.image
        )
        
        # Create activity record
        self._create_activity(
            design=design,
            user=user,
            activity_type='version',
            activity_data={
                'version_id': str(version.id),
                'version_number': version_number
            },
            description=f"Created version {version_number} of {design.title}",
            related_version=version
        )
        
        logger.info(f"Version {version_number} created for design {design.id} by {user.id}")
        return version
    
    def _can_comment(self, design: Design, user) -> bool:
        """Check if user can comment on a design"""
        # Owner can always comment
        if design.created_by == user:
            return True
        
        # Check if user has access through shares
        shares = DesignShare.objects.filter(
            design=design,
            shared_with=user,
            status='active',
            allow_comments=True,
            organization=design.organization
        )
        
        if shares.exists():
            return True
        
        # Check if user is in the same organization
        if user.current_organization == design.organization:
            from organizations.models import OrganizationMember
            try:
                membership = OrganizationMember.objects.get(
                    user=user,
                    organization=design.organization,
                    is_active=True
                )
                return membership.role in ['admin', 'manager', 'designer']
            except OrganizationMember.DoesNotExist:
                pass
        
        return False
    
    def _create_activity(
        self,
        design: Design,
        user,
        activity_type: str,
        activity_data: Dict[str, Any] = None,
        description: str = "",
        related_comment: DesignComment = None,
        related_collaboration: DesignCollaboration = None,
        related_version: DesignVersion = None
    ) -> DesignActivity:
        """Create an activity record"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        return DesignActivity.objects.create(
            organization=organization,
            design=design,
            user=user,
            activity_type=activity_type,
            activity_data=activity_data or {},
            description=description,
            related_comment=related_comment,
            related_collaboration=related_collaboration,
            related_version=related_version
        )
    
    def _send_share_notification(self, share: DesignShare, email: str):
        """Send email notification for design share"""
        try:
            subject = f"Design shared with you: {share.design.title}"
            
            # Create share URL
            if share.is_public:
                share_url = f"{self.base_url}/shared/{share.share_token}"
            else:
                share_url = f"{self.base_url}/designs/{share.design.id}"
            
            context = {
                'design_title': share.design.title,
                'shared_by_name': share.shared_by.get_full_name(),
                'access_level': share.get_access_level_display(),
                'share_url': share_url,
                'message': share.message,
                'expires_at': share.expires_at
            }
            
            html_message = render_to_string('collaboration/share_notification.html', context)
            plain_message = f"""
            {share.shared_by.get_full_name()} has shared a design with you.
            
            Design: {share.design.title}
            Access Level: {share.get_access_level_display()}
            URL: {share_url}
            
            {share.message if share.message else ''}
            """
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Share notification sent to {email} for design {share.design.id}")
            
        except Exception as e:
            logger.error(f"Failed to send share notification to {email}: {str(e)}")
    
    def get_design_activity(self, design: Design, limit: int = 50) -> List[DesignActivity]:
        """Get recent activity for a design"""
        return DesignActivity.objects.filter(
            design=design,
            organization=design.organization
        ).select_related('user', 'related_comment', 'related_collaboration', 'related_version').order_by('-created_at')[:limit]
    
    def get_user_activity(self, user, limit: int = 50) -> List[DesignActivity]:
        """Get recent activity for a user"""
        organization = get_current_organization()
        if not organization:
            return []
        
        return DesignActivity.objects.filter(
            user=user,
            organization=organization
        ).select_related('design', 'related_comment', 'related_collaboration', 'related_version').order_by('-created_at')[:limit]
