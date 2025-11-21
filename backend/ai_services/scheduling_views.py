"""
Scheduling system views for Phase 1 Week 3
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone as django_timezone

from .scheduling_models import ScheduledPost
from .serializers import (
    ScheduledPostSerializer, ScheduledPostCreateSerializer, 
    ScheduledPostUpdateSerializer
)
from .social_media import SocialMediaService
from organizations.middleware import get_current_organization, set_current_organization
from organizations.models import OrganizationMember, Organization

logger = logging.getLogger(__name__)


class ScheduledPostViewSet(viewsets.ModelViewSet):
    """ViewSet for managing scheduled posts"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ScheduledPostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ScheduledPostUpdateSerializer
        return ScheduledPostSerializer
    
    def _get_organization(self):
        """Get organization with fallback to user's organization"""
        # First try to get from request (set by middleware)
        organization = getattr(self.request, 'organization', None)
        if organization:
            logger.info(f"Got organization from request: {organization.name} (id: {organization.id})")
            return organization
        
        # Try to get from thread-local storage (set by middleware)
        organization = get_current_organization()
        if organization:
            logger.info(f"Got organization from thread-local: {organization.name} (id: {organization.id})")
            return organization
        
        # Fallback: get from user's active membership
        if hasattr(self.request, 'user') and self.request.user.is_authenticated:
            try:
                logger.info(f"Attempting to get organization from user {self.request.user.id} memberships")
                memberships = OrganizationMember.objects.filter(
                    user=self.request.user,
                    is_active=True
                ).select_related('organization')
                
                membership = memberships.first()
                if membership and membership.organization:
                    logger.info(f"Got organization from user membership: {membership.organization.name} (id: {membership.organization.id})")
                    # Set it on the request and thread-local for future use
                    self.request.organization = membership.organization
                    set_current_organization(membership.organization)
                    return membership.organization
                else:
                    logger.warning(f"User {self.request.user.id} ({getattr(self.request.user, 'email', 'no email')}) has no active organization memberships")
                    # Log all memberships for debugging
                    all_memberships = OrganizationMember.objects.filter(user=self.request.user).select_related('organization')
                    logger.warning(f"User {self.request.user.id} total memberships: {all_memberships.count()}")
                    for m in all_memberships:
                        logger.warning(f"  - Org: {m.organization.name if m.organization else 'None'}, Active: {m.is_active}, Role: {m.role}")
                    
                    # Try to get ANY membership (even inactive) to help debug
                    if all_memberships.count() == 0:
                        logger.warning(f"User {self.request.user.id} has NO organization memberships. Attempting to create default organization...")
                        # Try to create or get a default organization for the user
                        try:
                            from django.db import transaction
                            from django.utils.text import slugify
                            import uuid as uuid_lib
                            
                            # Generate a unique slug - use UUID to ensure uniqueness
                            user_id_str = str(self.request.user.id)
                            # Remove hyphens and take first 8 chars for shorter slug
                            user_id_short = user_id_str.replace('-', '')[:8] if '-' in user_id_str else user_id_str[:8]
                            base_slug = slugify(f"user-{user_id_short}-org")
                            if not base_slug or len(base_slug) < 3:
                                # Fallback to UUID-based slug if slugify fails
                                base_slug = f"org-{uuid_lib.uuid4().hex[:8]}"
                            
                            slug = base_slug
                            counter = 1
                            max_attempts = 10
                            while Organization.objects.filter(slug=slug).exists() and counter < max_attempts:
                                slug = f"{base_slug}-{counter}"
                                counter += 1
                            
                            if counter >= max_attempts:
                                # Use UUID as last resort
                                slug = f"org-{uuid_lib.uuid4().hex[:12]}"
                            
                            # Create organization and membership in a transaction
                            with transaction.atomic():
                                # Get user email/username safely
                                user_name = getattr(self.request.user, 'email', None) or getattr(self.request.user, 'username', None) or 'User'
                                org_name = f"{user_name}'s Organization"
                                
                                default_org = Organization.objects.create(
                                    slug=slug,
                                    name=org_name
                                )
                                
                                # Create membership
                                membership = OrganizationMember.objects.create(
                                    user=self.request.user,
                                    organization=default_org,
                                    role='admin',
                                    is_active=True
                                )
                            
                            logger.info(f"✅ Created default organization '{default_org.name}' (id: {default_org.id}, slug: {slug}) for user {self.request.user.id}")
                            self.request.organization = default_org
                            set_current_organization(default_org)
                            return default_org
                        except Exception as e:
                            logger.error(f"❌ Failed to create default organization: {e}", exc_info=True)
                            # Try to get any existing organization the user might own
                            try:
                                # Organization model doesn't have owner field, so check by membership instead
                                owned_org = None
                                # Try to get any organization where user is admin
                                admin_membership = OrganizationMember.objects.filter(
                                    user=self.request.user,
                                    role='admin'
                                ).select_related('organization').first()
                                if admin_membership:
                                    owned_org = admin_membership.organization
                                if owned_org:
                                    logger.info(f"Found existing organization '{owned_org.name}' owned by user {self.request.user.id}")
                                    # Create membership if it doesn't exist
                                    membership, created = OrganizationMember.objects.get_or_create(
                                        user=self.request.user,
                                        organization=owned_org,
                                        defaults={'role': 'admin', 'is_active': True}
                                    )
                                    if not membership.is_active:
                                        membership.is_active = True
                                        membership.save(update_fields=['is_active'])
                                    self.request.organization = owned_org
                                    set_current_organization(owned_org)
                                    return owned_org
                                else:
                                    logger.error(f"User {self.request.user.id} has no owned organizations either")
                            except Exception as e2:
                                logger.error(f"Failed to get owned organization: {e2}", exc_info=True)
                    else:
                        logger.warning(f"User {self.request.user.id} has memberships but none are active. Activating first membership...")
                        # Try to activate the first inactive membership
                        try:
                            first_membership = all_memberships.first()
                            if first_membership:
                                first_membership.is_active = True
                                first_membership.save(update_fields=['is_active'])
                                logger.info(f"Activated membership for user {self.request.user.id} in organization {first_membership.organization.name}")
                                self.request.organization = first_membership.organization
                                set_current_organization(first_membership.organization)
                                return first_membership.organization
                        except Exception as e:
                            logger.error(f"Failed to activate membership: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"Failed to get organization from user membership: {e}", exc_info=True)
        else:
            logger.warning(f"User is not authenticated. Has user attr: {hasattr(self.request, 'user')}, Is authenticated: {hasattr(self.request, 'user') and self.request.user.is_authenticated if hasattr(self.request, 'user') else False}")
        
        logger.error("No organization context available after all fallbacks")
        return None
    
    def get_queryset(self):
        """Return scheduled posts for current organization"""
        organization = self._get_organization()
        if not organization:
            return ScheduledPost.objects.none()
        
        queryset = ScheduledPost.objects.filter(organization=organization)
        
        # Filter by platform if provided
        platform = self.request.query_params.get('platform')
        if platform:
            queryset = queryset.filter(platform=platform)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(scheduled_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_time__lte=end_date)
        
        return queryset.select_related('user').order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Override create to handle ValueError and ValidationError properly"""
        try:
            logger.info(f"Creating scheduled post with data: {request.data}")
            logger.info(f"Request method: {request.method}, Path: {request.path}")
            logger.info(f"User authenticated: {hasattr(request, 'user') and request.user.is_authenticated}")
            if hasattr(request, 'user') and request.user.is_authenticated:
                logger.info(f"User ID: {request.user.id}, Email: {getattr(request.user, 'email', 'no email')}")
            else:
                logger.warning("User is not authenticated!")
            
            # Check organization before proceeding - this will auto-create if needed
            organization = self._get_organization()
            if not organization:
                # Last resort: In development, try to create organization for any user
                from django.conf import settings
                if settings.DEBUG and hasattr(request, 'user') and request.user.is_authenticated:
                    logger.warning("Last resort: Attempting to force-create organization in DEBUG mode")
                    try:
                        from django.db import transaction
                        import uuid as uuid_lib
                        from django.utils.text import slugify
                        
                        # Generate unique slug
                        slug = f"dev-org-{uuid_lib.uuid4().hex[:12]}"
                        user_name = getattr(request.user, 'email', None) or getattr(request.user, 'username', None) or 'User'
                        
                        with transaction.atomic():
                            default_org = Organization.objects.create(
                                slug=slug,
                                name=f"{user_name}'s Organization"
                            )
                            
                            membership, created = OrganizationMember.objects.get_or_create(
                                user=request.user,
                                organization=default_org,
                                defaults={'role': 'admin', 'is_active': True}
                            )
                            if not membership.is_active:
                                membership.is_active = True
                                membership.save(update_fields=['is_active'])
                        
                        logger.info(f"✅ Force-created organization in DEBUG mode: {default_org.name} (id: {default_org.id})")
                        request.organization = default_org
                        set_current_organization(default_org)
                        organization = default_org
                    except Exception as e:
                        logger.error(f"❌ Even force-creation failed: {e}", exc_info=True)
                
                if not organization:
                    user_info = f"user {request.user.id}" if hasattr(request, 'user') and request.user.is_authenticated else "anonymous user"
                    logger.error(f"No organization found for {user_info} after all attempts including auto-creation and force-creation")
                    return Response(
                        {
                            "success": False,
                            "error": "Unable to set up organization context. Please contact support or ensure you are logged in.",
                            "detail": "Unable to set up organization context. Please contact support or ensure you are logged in.",
                            "debug_info": {
                                "user_authenticated": hasattr(request, 'user') and request.user.is_authenticated,
                                "user_id": getattr(request.user, 'id', None) if hasattr(request, 'user') else None,
                                "user_email": getattr(request.user, 'email', None) if hasattr(request, 'user') else None
                            } if settings.DEBUG else {}
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            logger.info(f"Organization context: {organization.name} (id: {organization.id})")
            
            # Create serializer and validate
            serializer = self.get_serializer(data=request.data)
            logger.info(f"Serializer created, validating data...")
            if not serializer.is_valid():
                logger.error(f"Serializer validation failed: {serializer.errors}")
                return Response(
                    {
                        "success": False,
                        "error": "Validation failed",
                        "detail": serializer.errors,
                        "message": "Please check the form fields for errors"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            logger.info(f"Serializer validation passed")
            
            return super().create(request, *args, **kwargs)
        except DRFValidationError as e:
            logger.error(f"ValidationError in create: {e.detail}")
            # Format validation errors properly
            error_detail = e.detail
            if isinstance(error_detail, dict):
                # If it's a dict of field errors, format them nicely
                formatted_errors = {}
                for field, errors in error_detail.items():
                    if isinstance(errors, list):
                        formatted_errors[field] = errors[0] if len(errors) == 1 else errors
                    else:
                        formatted_errors[field] = errors
                return Response(
                    {
                        "success": False,
                        "error": "Validation failed",
                        "detail": formatted_errors,
                        "message": "Please check the form fields for errors"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                error_message = str(error_detail) if error_detail else "Validation failed"
                return Response(
                    {
                        "success": False,
                        "error": error_message,
                        "detail": error_message
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError as e:
            logger.error(f"ValueError in create: {str(e)}")
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "detail": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Unexpected error in create: {str(e)}", exc_info=True)
            # Don't expose internal error details to client
            error_message = "Failed to create scheduled post"
            if "organization" in str(e).lower():
                error_message = "No organization context available. Please ensure you are a member of an organization."
            return Response(
                {
                    "success": False,
                    "error": error_message,
                    "detail": error_message
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def perform_create(self, serializer):
        """Create scheduled post with proper organization and user"""
        organization = self._get_organization()
        if not organization:
            raise ValueError("No organization context available. Please ensure you are a member of an organization.")
        
        # Validate scheduled time is in the future
        scheduled_time = serializer.validated_data['scheduled_time']
        if scheduled_time <= timezone.now():
            raise ValueError("Scheduled time must be in the future")
        
        # Create the scheduled post
        scheduled_post = serializer.save(
            organization=organization,
            user=self.request.user,
            status='pending'
        )
        
        # Schedule the post for processing
        self._schedule_post_processing(scheduled_post)
        
        logger.info(f"Created scheduled post {scheduled_post.id} for {scheduled_post.platform}")
    
    def perform_update(self, serializer):
        """Update scheduled post"""
        scheduled_post = self.get_object()
        
        # Only allow updates for pending or scheduled posts
        if scheduled_post.status not in ['pending', 'scheduled']:
            raise ValueError("Cannot update posts that are already posted, failed, or cancelled")
        
        # Validate scheduled time is in the future
        if 'scheduled_time' in serializer.validated_data:
            scheduled_time = serializer.validated_data['scheduled_time']
            if scheduled_time <= timezone.now():
                raise ValueError("Scheduled time must be in the future")
        
        # Update the post
        serializer.save()
        
        # Reschedule if needed
        if scheduled_post.status == 'scheduled':
            self._schedule_post_processing(scheduled_post)
        
        logger.info(f"Updated scheduled post {scheduled_post.id}")
    
    def perform_destroy(self, instance):
        """Delete/cancel scheduled post"""
        # Only allow deletion of posts that haven't been posted yet
        if instance.status == 'posted':
            raise ValueError("Cannot delete posts that have already been posted")
        
        # For pending/scheduled posts, cancel them (soft delete)
        # For failed/cancelled posts, we can actually delete them
        if instance.status in ['failed', 'cancelled']:
            # Actually delete if already cancelled/failed
            logger.info(f"Deleting scheduled post {instance.id} (status: {instance.status})")
            instance.delete()
        else:
            # Soft delete by cancelling
            instance.status = 'cancelled'
            instance.save(update_fields=['status'])
            logger.info(f"Cancelled scheduled post {instance.id}")
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a scheduled post"""
        scheduled_post = self.get_object()
        
        if scheduled_post.status in ['posted']:
            return Response(
                {"error": "Cannot cancel posts that have already been posted"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        scheduled_post.status = 'cancelled'
        scheduled_post.save(update_fields=['status'])
        
        serializer = self.get_serializer(scheduled_post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed scheduled post"""
        scheduled_post = self.get_object()
        
        if scheduled_post.status != 'failed':
            return Response(
                {"error": "Can only retry failed posts"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not scheduled_post.can_retry():
            return Response(
                {"error": "Maximum retry attempts exceeded"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset for retry
        scheduled_post.status = 'pending'
        scheduled_post.error_message = None
        scheduled_post.save(update_fields=['status', 'error_message'])
        
        # Schedule for processing
        self._schedule_post_processing(scheduled_post)
        
        serializer = self.get_serializer(scheduled_post)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def ready_to_post(self, request):
        """Get posts that are ready to be posted"""
        organization = self._get_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get posts that are ready to be posted
        ready_posts = ScheduledPost.objects.filter(
            organization=organization,
            status='scheduled',
            scheduled_time__lte=timezone.now()
        )
        
        serializer = self.get_serializer(ready_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def process_ready_posts(self, request):
        """Process all ready-to-post scheduled posts"""
        organization = self._get_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get posts that are ready to be posted
        ready_posts = ScheduledPost.objects.filter(
            organization=organization,
            status='scheduled',
            scheduled_time__lte=timezone.now()
        )
        
        results = []
        for post in ready_posts:
            try:
                result = self._process_scheduled_post(post)
                results.append({
                    'post_id': str(post.id),
                    'platform': post.platform,
                    'success': result['success'],
                    'message': result.get('message', '')
                })
            except Exception as e:
                logger.error(f"Failed to process scheduled post {post.id}: {str(e)}")
                results.append({
                    'post_id': str(post.id),
                    'platform': post.platform,
                    'success': False,
                    'message': str(e)
                })
        
        return Response({
            'processed_count': len(results),
            'results': results
        }, status=status.HTTP_200_OK)
    
    def _schedule_post_processing(self, scheduled_post):
        """
        Schedule a post for processing
        TODO: Implement actual scheduling with Celery or Django-Q
        """
        # For now, just mark as scheduled
        # In real implementation, this would schedule a Celery task
        scheduled_post.status = 'scheduled'
        scheduled_post.save(update_fields=['status'])
        
        logger.info(f"Scheduled post {scheduled_post.id} for processing at {scheduled_post.scheduled_time}")
    
    def _process_scheduled_post(self, scheduled_post):
        """
        Process a scheduled post by posting to social media
        """
        try:
            # Get social media service
            social_service = SocialMediaService()
            
            # Post to the specified platform
            result = social_service.post_to_platform(
                platform=scheduled_post.platform,
                asset_url=scheduled_post.asset_url,
                caption=scheduled_post.caption,
                **scheduled_post.metadata
            )
            
            if result['success']:
                # Mark as posted
                scheduled_post.mark_as_posted()
                logger.info(f"Successfully posted {scheduled_post.id} to {scheduled_post.platform}")
                return {
                    'success': True,
                    'message': f"Successfully posted to {scheduled_post.platform}",
                    'post_id': result.get('post_id'),
                    'url': result.get('url')
                }
            else:
                # Mark as failed
                scheduled_post.mark_as_failed(result.get('error', 'Unknown error'))
                logger.error(f"Failed to post {scheduled_post.id}: {result.get('error')}")
                return {
                    'success': False,
                    'message': result.get('error', 'Unknown error')
                }
                
        except Exception as e:
            # Mark as failed
            scheduled_post.mark_as_failed(str(e))
            logger.error(f"Exception while processing scheduled post {scheduled_post.id}: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get scheduling analytics"""
        organization = self._get_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timezone.timedelta(days=days)
        
        # Get posts in date range
        posts = ScheduledPost.objects.filter(
            organization=organization,
            created_at__gte=start_date
        )
        
        # Calculate analytics
        total_posts = posts.count()
        posted_posts = posts.filter(status='posted').count()
        failed_posts = posts.filter(status='failed').count()
        pending_posts = posts.filter(status__in=['pending', 'scheduled']).count()
        cancelled_posts = posts.filter(status='cancelled').count()
        
        # Platform breakdown
        platform_breakdown = {}
        for platform, _ in ScheduledPost.PLATFORM_CHOICES:
            platform_breakdown[platform] = posts.filter(platform=platform).count()
        
        # Status breakdown
        status_breakdown = {}
        for status_choice, _ in ScheduledPost.STATUS_CHOICES:
            status_breakdown[status_choice] = posts.filter(status=status_choice).count()
        
        analytics_data = {
            'total_posts': total_posts,
            'posted_posts': posted_posts,
            'failed_posts': failed_posts,
            'pending_posts': pending_posts,
            'cancelled_posts': cancelled_posts,
            'success_rate': round((posted_posts / total_posts * 100) if total_posts > 0 else 0, 2),
            'platform_breakdown': platform_breakdown,
            'status_breakdown': status_breakdown,
            'date_range': {
                'start_date': start_date.isoformat(),
                'end_date': timezone.now().isoformat(),
                'days': days
            }
        }
        
        return Response(analytics_data, status=status.HTTP_200_OK)
