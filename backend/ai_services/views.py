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
# Removed image generation imports

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


class TextGenerationViewSet(viewsets.ViewSet):
    """ViewSet for Text Generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def generate_text(self, request):
        """Generate text content using AI"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        prompt = request.data.get('prompt')
        context = request.data.get('context', '')
        style = request.data.get('style', 'professional')
        length = request.data.get('length', 'medium')
        
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create AI generation request
            from .models import AIGenerationRequest, AIProvider
            
            # Get or create a Gemini provider
            provider, created = AIProvider.objects.get_or_create(
                name='gemini',
                defaults={'is_active': True}
            )
            
            # Create the request
            ai_request = AIGenerationRequest.objects.create(
                organization=organization,
                user=request.user,
                provider=provider,
                generation_type='text_generation',
                prompt=prompt,
                parameters={
                    'context': context,
                    'style': style,
                    'length': length
                }
            )
            
            # Process the request
            ai_service = AIGenerationService()
            success = ai_service.process_generation_request(ai_request)
            
            if success:
                return Response({
                    "success": True,
                    "generated_text": ai_request.result_text,
                    "request_id": str(ai_request.id),
                    "metadata": {
                        "generated_at": ai_request.completed_at.isoformat() if ai_request.completed_at else None,
                        "processing_time": ai_request.processing_time,
                        "cost": float(ai_request.cost) if ai_request.cost else 0
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": ai_request.error_message or "Generation failed"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            return Response(
                {"error": f"Text generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContentAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for Content Analysis"""
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def analyze_content(self, request):
        """Analyze content using AI"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        content = request.data.get('content')
        analysis_type = request.data.get('analysis_type', 'general')
        
        if not content:
            return Response(
                {"error": "Content is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create AI generation request
            from .models import AIGenerationRequest, AIProvider
            
            # Get or create a Gemini provider
            provider, created = AIProvider.objects.get_or_create(
                name='gemini',
                defaults={'is_active': True}
            )
            
            # Create the request
            ai_request = AIGenerationRequest.objects.create(
                organization=organization,
                user=request.user,
                provider=provider,
                generation_type='content_analysis',
                prompt=content,
                parameters={
                    'analysis_type': analysis_type
                }
            )
            
            # Process the request
            ai_service = AIGenerationService()
            success = ai_service.process_generation_request(ai_request)
            
            if success:
                return Response({
                    "success": True,
                    "analysis_result": ai_request.result_text,
                    "request_id": str(ai_request.id),
                    "metadata": {
                        "generated_at": ai_request.completed_at.isoformat() if ai_request.completed_at else None,
                        "processing_time": ai_request.processing_time,
                        "cost": float(ai_request.cost) if ai_request.cost else 0
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": ai_request.error_message or "Analysis failed"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Content analysis failed: {str(e)}")
            return Response(
                {"error": f"Content analysis failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
