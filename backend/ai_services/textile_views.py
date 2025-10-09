"""
Textile-specific AI endpoints for Phase 1 Week 3
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.conf import settings

from .models import AIGenerationRequest, AIProvider, AIUsageQuota
from .serializers import (
    TextilePosterRequestSerializer, TextileCaptionRequestSerializer,
    TextilePosterResponseSerializer, TextileCaptionResponseSerializer
)
from .services import AIGenerationService
from .poster_generator import TextilePosterGenerator
from .arcjet_service import ArcjetService
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class TextilePosterViewSet(viewsets.ViewSet):
    """ViewSet for textile poster generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poster_generator = TextilePosterGenerator()
        self.ai_service = AIGenerationService()
        self.arcjet_service = ArcjetService()
    
    @action(detail=False, methods=['post'])
    def generate_poster(self, request):
        """
        Generate AI poster for textile product
        
        POST /api/textile/poster/
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = TextilePosterRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Check Arcjet limits
            limit_check = self.arcjet_service.check_usage_limit(organization, 'poster_generation')
            if not limit_check['within_limits']:
                return Response(
                    {
                        "error": "Usage limit exceeded. Please upgrade your plan.",
                        "details": {
                            "plan": limit_check.get('plan', 'unknown'),
                            "monthly_exceeded": limit_check.get('monthly_exceeded', False),
                            "daily_exceeded": limit_check.get('daily_exceeded', False),
                            "remaining_monthly": limit_check.get('remaining_monthly', 0),
                            "remaining_daily": limit_check.get('remaining_daily', 0)
                        }
                    }, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Generate poster using AI service
            result = self.poster_generator.generate_poster_with_caption(
                organization=organization,
                user=request.user,
                fabric_image_url=data['product_image_url'],
                fabric_type=data['fabric_type'],
                festival=data['festival'],
                price_range=data['price_range'],
                style=data['style'],
                color_scheme=data.get('color_scheme'),
                custom_text=data.get('custom_text'),
                offer_details=data.get('offer_details')
            )
            
            # Format response with cache-busting
            import time
            timestamp = int(time.time() * 1000)
            
            # Add cache-busting parameter to poster URL if it exists
            poster_url = result.get('poster_url', '')
            if poster_url and '?' not in poster_url:
                poster_url += f'?t={timestamp}'
            elif poster_url and '?' in poster_url:
                poster_url += f'&t={timestamp}'
            
            response_data = {
                'success': True,
                'poster_url': poster_url,
                'caption_suggestions': result.get('caption_suggestions', []),
                'hashtags': result.get('hashtags', []),
                'cache_bust': timestamp,  # Add cache-busting timestamp
                'metadata': {
                    'fabric_type': data['fabric_type'],
                    'festival': data['festival'],
                    'style': data['style'],
                    'generated_at': timezone.now().isoformat(),
                    'organization': organization.name,
                    'unique_id': f"gen_{timestamp}"  # Add unique ID
                }
            }
            
            # Increment usage counter
            self.arcjet_service.increment_usage(organization, 'poster_generation')
            
            # Validate response
            response_serializer = TextilePosterResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Response validation failed: {response_serializer.errors}")
                return Response(
                    {"error": "Invalid response format"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Poster generation failed: {str(e)}")
            return Response(
                {"error": f"Poster generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class TextileCaptionViewSet(viewsets.ViewSet):
    """ViewSet for textile caption generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poster_generator = TextilePosterGenerator()
        self.ai_service = AIGenerationService()
        self.arcjet_service = ArcjetService()
    
    @action(detail=False, methods=['post'])
    def generate_caption(self, request):
        """
        Generate AI caption and hashtags for textile product
        
        POST /api/textile/caption/
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context available"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = TextileCaptionRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        try:
            # Check Arcjet limits
            limit_check = self.arcjet_service.check_usage_limit(organization, 'caption_generation')
            if not limit_check['within_limits']:
                return Response(
                    {
                        "error": "Usage limit exceeded. Please upgrade your plan.",
                        "details": {
                            "plan": limit_check.get('plan', 'unknown'),
                            "monthly_exceeded": limit_check.get('monthly_exceeded', False),
                            "daily_exceeded": limit_check.get('daily_exceeded', False),
                            "remaining_monthly": limit_check.get('remaining_monthly', 0),
                            "remaining_daily": limit_check.get('remaining_daily', 0)
                        }
                    }, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Generate captions using AI service
            captions = self.poster_generator.generate_caption_suggestions(
                fabric_type=data['fabric_type'],
                festival=data.get('festival'),
                price_range=data['price_range'],
                style=data['style'],
                custom_text=data.get('custom_text'),
                product_name=data['product_name'],
                offer_details=data.get('offer_details')
            )
            
            # Generate hashtags
            hashtags = self._generate_hashtags(
                fabric_type=data['fabric_type'],
                festival=data.get('festival'),
                style=data['style']
            )
            
            # Format response with cache-busting
            import time
            timestamp = int(time.time() * 1000)
            
            response_data = {
                'success': True,
                'captions': captions,
                'hashtags': hashtags,
                'cache_bust': timestamp,  # Add cache-busting timestamp
                'metadata': {
                    'product_name': data['product_name'],
                    'fabric_type': data['fabric_type'],
                    'festival': data.get('festival'),
                    'style': data['style'],
                    'generated_at': timezone.now().isoformat(),
                    'organization': organization.name
                }
            }
            
            # Increment usage counter
            self.arcjet_service.increment_usage(organization, 'caption_generation')
            
            # Validate response
            response_serializer = TextileCaptionResponseSerializer(data=response_data)
            if response_serializer.is_valid():
                return Response(response_serializer.validated_data, status=status.HTTP_200_OK)
            else:
                logger.error(f"Response validation failed: {response_serializer.errors}")
                return Response(
                    {"error": "Invalid response format"}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
        except Exception as e:
            logger.error(f"Caption generation failed: {str(e)}")
            return Response(
                {"error": f"Caption generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_hashtags(self, fabric_type, festival=None, style=None):
        """Generate relevant hashtags"""
        hashtags = []
        
        # Fabric type hashtags
        fabric_hashtags = {
            'saree': ['#saree', '#silk', '#traditional', '#indianwear'],
            'cotton': ['#cotton', '#natural', '#comfortable', '#breathable'],
            'silk': ['#silk', '#luxury', '#elegant', '#premium'],
            'linen': ['#linen', '#natural', '#sustainable', '#comfortable']
        }
        
        if fabric_type.lower() in fabric_hashtags:
            hashtags.extend(fabric_hashtags[fabric_type.lower()])
        
        # Festival hashtags
        if festival:
            festival_hashtags = {
                'deepavali': ['#deepavali', '#diwali', '#festival', '#celebration'],
                'pongal': ['#pongal', '#harvest', '#festival', '#traditional'],
                'wedding': ['#wedding', '#bridal', '#celebration', '#special']
            }
            if festival.lower() in festival_hashtags:
                hashtags.extend(festival_hashtags[festival.lower()])
        
        # Style hashtags
        if style:
            style_hashtags = {
                'elegant': ['#elegant', '#sophisticated', '#classy'],
                'modern': ['#modern', '#contemporary', '#trendy'],
                'traditional': ['#traditional', '#heritage', '#classic'],
                'bohemian': ['#bohemian', '#boho', '#artistic']
            }
            if style.lower() in style_hashtags:
                hashtags.extend(style_hashtags[style.lower()])
        
        # General textile hashtags
        hashtags.extend(['#textile', '#fashion', '#style', '#design'])
        
        # Remove duplicates and limit to 20 hashtags
        return list(set(hashtags))[:20]
