"""
Social Media Posting Views
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from .social_media import SocialMediaService
from .serializers import SocialMediaPostSerializer, SocialMediaPostResponseSerializer
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class SocialMediaPostViewSet(viewsets.ViewSet):
    """ViewSet for social media posting"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.social_service = SocialMediaService()
    
    @action(detail=False, methods=['post'])
    def post_to_platform(self, request):
        """
        Post to social media platform
        
        POST /api/ai/social/post/
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = SocialMediaPostSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Post to platform using social media service
            result = self.social_service.post_to_platform(
                platform=data['platform'],
                asset_url=data['asset_url'],
                caption=data['caption'],
                **data.get('metadata', {})
            )
            
            # Format response
            response_data = {
                'success': result['success'],
                'platform': data['platform'],
                'post_id': result.get('post_id'),
                'url': result.get('url'),
                'message': result.get('message', ''),
                'posted_at': timezone.now().isoformat(),
                'organization': organization.name
            }
            
            # Validate response
            response_serializer = SocialMediaPostResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Response validation failed: {response_serializer.errors}")
                return Response(
                    {"error": "Invalid response format"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Social media posting failed: {str(e)}")
            return Response(
                {"error": f"Social media posting failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def supported_platforms(self, request):
        """
        Get list of supported platforms
        
        GET /api/ai/social/platforms/
        """
        try:
            platforms = self.social_service.get_supported_platforms()
            
            # Get platform requirements
            platform_info = []
            for platform in platforms:
                requirements = self.social_service.get_platform_requirements(platform)
                platform_info.append({
                    'name': platform,
                    'display_name': platform.title(),
                    'requirements': requirements
                })
            
            return Response({
                'success': True,
                'platforms': platform_info,
                'total_platforms': len(platforms)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Get supported platforms failed: {str(e)}")
            return Response(
                {"error": f"Get supported platforms failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def validate_platform(self, request):
        """
        Validate platform configuration
        
        POST /api/ai/social/validate/
        """
        try:
            platform = request.data.get('platform')
            if not platform:
                return Response(
                    {"error": "Platform is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            is_valid = self.social_service.validate_platform(platform)
            requirements = self.social_service.get_platform_requirements(platform)
            
            return Response({
                'success': True,
                'platform': platform,
                'is_valid': is_valid,
                'requirements': requirements
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Platform validation failed: {str(e)}")
            return Response(
                {"error": f"Platform validation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def test_connection(self, request):
        """
        Test connection to social media platform
        
        POST /api/ai/social/test/
        """
        try:
            platform = request.data.get('platform')
            if not platform:
                return Response(
                    {"error": "Platform is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Test with a mock post
            result = self.social_service.post_to_platform(
                platform=platform,
                asset_url="https://example.com/test-image.jpg",
                caption="Test post from Frameio AI Services",
                test_mode=True
            )
            
            return Response({
                'success': result['success'],
                'platform': platform,
                'message': result.get('message', ''),
                'tested_at': timezone.now().isoformat()
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return Response(
                {"error": f"Connection test failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
