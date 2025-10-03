"""
Scheduling system views for Phase 1 Week 3
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from django.utils import timezone as django_timezone

from .scheduling_models import ScheduledPost
from .serializers import (
    ScheduledPostSerializer, ScheduledPostCreateSerializer, 
    ScheduledPostUpdateSerializer
)
from .social_media import SocialMediaService
from organizations.middleware import get_current_organization

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
    
    def get_queryset(self):
        """Return scheduled posts for current organization"""
        organization = get_current_organization()
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
    
    def perform_create(self, serializer):
        """Create scheduled post with proper organization and user"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
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
        """Cancel scheduled post"""
        if instance.status in ['posted']:
            raise ValueError("Cannot cancel posts that have already been posted")
        
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
        organization = get_current_organization()
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
        organization = get_current_organization()
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
        organization = get_current_organization()
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
