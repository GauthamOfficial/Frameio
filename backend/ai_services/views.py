from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
import logging

from .models import (
    AIProvider, AIGenerationRequest, AIUsageQuota, 
    AITemplate, AIGenerationHistory
)
from .serializers import (
    AIProviderSerializer, AIGenerationRequestSerializer, 
    AIGenerationRequestCreateSerializer, AIUsageQuotaSerializer,
    AITemplateSerializer, AITemplatePublicSerializer,
    AIGenerationHistorySerializer, AIAnalyticsSerializer
)
from organizations.middleware import get_current_organization
from .services import AIGenerationService
from .poster_generator import TextilePosterGenerator, FestivalKitGenerator
from .catalog_builder import TextileCatalogBuilder
from .background_matcher import BackgroundMatcher, FabricColorDetector

logger = logging.getLogger(__name__)


class AIProviderViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Providers - read-only for users"""
    serializer_class = AIProviderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return only active providers"""
        return AIProvider.objects.filter(is_active=True)


class AIGenerationRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for AI Generation Requests"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return AIGenerationRequestCreateSerializer
        return AIGenerationRequestSerializer
    
    def get_queryset(self):
        """Return requests for current organization"""
        # Get organization from request (set by TenantMiddleware)
        organization = getattr(self.request, 'organization', None)
        if not organization:
            # Fallback to get_current_organization for backward compatibility
            organization = get_current_organization()
            if not organization:
                return AIGenerationRequest.objects.none()
        
        queryset = AIGenerationRequest.objects.filter(organization=organization)
        
        # Filter by generation type if provided
        generation_type = self.request.query_params.get('generation_type')
        if generation_type:
            queryset = queryset.filter(generation_type=generation_type)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.select_related('provider', 'user').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create AI generation request with proper organization and user"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Check quota before creating request
        provider = serializer.validated_data['provider']
        generation_type = serializer.validated_data['generation_type']
        
        # Check if quota is exceeded
        quota = AIUsageQuota.objects.filter(
            organization=organization,
            provider=provider,
            generation_type=generation_type,
            quota_type='monthly'
        ).first()
        
        if quota and quota.is_quota_exceeded():
            raise ValueError("Monthly quota exceeded for this generation type")
        
        # Save the request
        request_obj = serializer.save(
            organization=organization,
            user=self.request.user
        )
        
        # Process the request asynchronously
        try:
            ai_service = AIGenerationService()
            ai_service.process_generation_request(request_obj)
        except Exception as e:
            logger.error(f"Failed to process AI generation request {request_obj.id}: {str(e)}")
            request_obj.mark_failed(str(e))


class AIUsageQuotaViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for AI Usage Quotas - read-only for users"""
    serializer_class = AIUsageQuotaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return quotas for current organization"""
        organization = get_current_organization()
        if not organization:
            return AIUsageQuota.objects.none()
        
        return AIUsageQuota.objects.filter(organization=organization).select_related('provider')


class AITemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for AI Templates"""
    serializer_class = AITemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return templates for current organization and public templates"""
        organization = get_current_organization()
        if not organization:
            return AITemplate.objects.none()
        
        queryset = AITemplate.objects.filter(
            Q(organization=organization) | Q(is_public=True, is_active=True)
        )
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset.order_by('-usage_count', 'name')
    
    def perform_create(self, serializer):
        """Create template with current organization"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        serializer.save(organization=organization)


class AIAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for AI Analytics"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get AI analytics dashboard data"""
        # Get organization from request (set by TenantMiddleware)
        organization = getattr(request, 'organization', None)
        if not organization:
            # Fallback to get_current_organization for backward compatibility
            organization = get_current_organization()
            if not organization:
                # For testing, try to get organization from authenticated user
                if hasattr(request, 'user') and request.user.is_authenticated:
                    organization = request.user.current_organization
                    if not organization:
                        # Get first organization the user belongs to
                        memberships = request.user.organization_memberships.filter(is_active=True)
                        if memberships.exists():
                            organization = memberships.first().organization
                
                if not organization:
                    return Response(
                        {"error": "No organization context"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        # Get date range from query params
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        # Get requests in date range
        requests = AIGenerationRequest.objects.filter(
            organization=organization,
            created_at__gte=start_date
        )
        
        # Calculate metrics
        total_requests = requests.count()
        successful_requests = requests.filter(status='completed').count()
        failed_requests = requests.filter(status='failed').count()
        success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
        
        # Average processing time
        avg_processing_time = requests.filter(
            status='completed',
            processing_time__isnull=False
        ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0
        
        # Total cost
        total_cost = requests.aggregate(total=Sum('cost'))['total'] or 0
        
        analytics_data = {
            'total_requests': total_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': round(success_rate, 2),
            'average_processing_time': round(avg_processing_time, 2),
            'total_cost': total_cost,
            'most_used_generation_type': None,
            'most_used_provider': None,
            'quota_usage_by_type': {}
        }
        
        serializer = AIAnalyticsSerializer(analytics_data)
        return Response(serializer.data)


class TextilePosterViewSet(viewsets.ViewSet):
    """ViewSet for Textile Poster Generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.poster_generator = TextilePosterGenerator()
    
    @action(detail=False, methods=['post'])
    def generate_poster(self, request):
        """Generate textile poster with AI caption suggestions"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract parameters from request
        fabric_image_url = request.data.get('fabric_image_url')
        fabric_type = request.data.get('fabric_type', 'saree')
        festival = request.data.get('festival', 'deepavali')
        price_range = request.data.get('price_range', '₹2999')
        style = request.data.get('style', 'elegant')
        color_scheme = request.data.get('color_scheme')
        custom_text = request.data.get('custom_text')
        
        try:
            result = self.poster_generator.generate_poster_with_caption(
                organization=organization,
                user=request.user,
                fabric_image_url=fabric_image_url,
                fabric_type=fabric_type,
                festival=festival,
                price_range=price_range,
                style=style,
                color_scheme=color_scheme,
                custom_text=custom_text
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Poster generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_captions(self, request):
        """Generate AI caption suggestions only"""
        fabric_type = request.data.get('fabric_type', 'saree')
        festival = request.data.get('festival')
        price_range = request.data.get('price_range', '₹2999')
        style = request.data.get('style', 'elegant')
        custom_text = request.data.get('custom_text')
        
        try:
            captions = self.poster_generator.generate_caption_suggestions(
                fabric_type=fabric_type,
                festival=festival,
                price_range=price_range,
                style=style,
                custom_text=custom_text
            )
            
            return Response({
                'success': True,
                'caption_suggestions': captions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Caption generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available poster templates"""
        try:
            templates = self.poster_generator.get_poster_templates()
            return Response({
                'success': True,
                'templates': templates
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get poster templates: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class FestivalKitViewSet(viewsets.ViewSet):
    """ViewSet for Festival Kit Generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.festival_generator = FestivalKitGenerator()
    
    @action(detail=False, methods=['post'])
    def generate_kit(self, request):
        """Generate complete festival kit"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        festival = request.data.get('festival', 'deepavali')
        fabric_types = request.data.get('fabric_types', ['saree', 'silk', 'cotton'])
        color_schemes = request.data.get('color_schemes', ['golden', 'red and gold', 'traditional'])
        price_ranges = request.data.get('price_ranges', ['₹1999', '₹2999', '₹4999'])
        
        try:
            result = self.festival_generator.generate_festival_kit(
                organization=organization,
                user=request.user,
                festival=festival,
                fabric_types=fabric_types,
                color_schemes=color_schemes,
                price_ranges=price_ranges
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Festival kit generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def themes(self, request):
        """Get festival themes"""
        festival = request.query_params.get('festival', 'deepavali')
        
        try:
            themes = self.festival_generator.get_festival_themes(festival)
            color_palettes = self.festival_generator.get_festival_color_palettes(festival)
            
            return Response({
                'success': True,
                'festival': festival,
                'themes': themes,
                'color_palettes': color_palettes
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get festival themes: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CatalogBuilderViewSet(viewsets.ViewSet):
    """ViewSet for Catalog Builder"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.catalog_builder = TextileCatalogBuilder()
    
    @action(detail=False, methods=['post'])
    def build_catalog(self, request):
        """Build catalog with AI descriptions"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        products = request.data.get('products', [])
        catalog_style = request.data.get('catalog_style', 'modern')
        layout_type = request.data.get('layout_type', 'grid')
        theme = request.data.get('theme', 'professional')
        auto_generate_descriptions = request.data.get('auto_generate_descriptions', True)
        
        try:
            result = self.catalog_builder.build_catalog_with_ai_descriptions(
                organization=organization,
                user=request.user,
                products=products,
                catalog_style=catalog_style,
                layout_type=layout_type,
                theme=theme,
                auto_generate_descriptions=auto_generate_descriptions
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Catalog building failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_description(self, request):
        """Generate AI description for a single product"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        product_info = request.data.get('product_info', {})
        
        try:
            result = self.catalog_builder.generate_product_description(
                organization=organization,
                user=request.user,
                product_info=product_info
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Product description generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available catalog templates"""
        try:
            templates = self.catalog_builder.get_catalog_templates()
            return Response({
                'success': True,
                'templates': templates
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get catalog templates: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """Export catalog data"""
        format_type = request.query_params.get('format', 'json')
        
        try:
            result = self.catalog_builder.export_catalog_data(pk, format_type)
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Catalog export failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BackgroundMatcherViewSet(viewsets.ViewSet):
    """ViewSet for Background Matching"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_matcher = BackgroundMatcher()
        self.color_detector = FabricColorDetector()
    
    @action(detail=False, methods=['post'])
    def generate_background(self, request):
        """Generate matching background for fabric"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "No organization context"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_image_url = request.data.get('fabric_image_url')
        background_style = request.data.get('background_style', 'complementary')
        pattern_type = request.data.get('pattern_type', 'seamless')
        intensity = request.data.get('intensity', 'medium')
        
        if not fabric_image_url:
            return Response(
                {"error": "fabric_image_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.background_matcher.generate_matching_background(
                organization=organization,
                user=request.user,
                fabric_image_url=fabric_image_url,
                background_style=background_style,
                pattern_type=pattern_type,
                intensity=intensity
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Background generation failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def analyze_colors(self, request):
        """Analyze fabric colors"""
        fabric_image_url = request.data.get('fabric_image_url')
        
        if not fabric_image_url:
            return Response(
                {"error": "fabric_image_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = self.color_detector.analyze_fabric_colors(fabric_image_url)
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Color analysis failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def presets(self, request):
        """Get background presets"""
        try:
            presets = self.background_matcher.get_background_presets()
            return Response({
                'success': True,
                'presets': presets
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get background presets: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
