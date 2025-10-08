"""
Fabric Analysis Views for Phase 1 Week 4
API endpoints for fabric color extraction and texture analysis
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction

from .models import AIGenerationRequest, AIProvider, AIUsageQuota
from .fabric_analysis import FabricAnalyzer
from .color_matching import SmartColorMatcher
from .services import AIGenerationService
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class FabricAnalysisViewSet(viewsets.ViewSet):
    """ViewSet for Fabric Analysis endpoints"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fabric_analyzer = FabricAnalyzer()
        self.color_matcher = SmartColorMatcher()
        self.ai_service = AIGenerationService()
    
    @action(detail=False, methods=['post'])
    def analyze_fabric(self, request):
        """
        Comprehensive fabric analysis endpoint
        POST /api/ai-services/fabric/analyze-fabric/
        
        Body:
        {
            "fabric_image_url": "https://example.com/fabric.jpg",
            "analysis_type": "comprehensive"  // "comprehensive", "colors_only", "texture_only"
        }
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_image_url = request.data.get('fabric_image_url')
        analysis_type = request.data.get('analysis_type', 'comprehensive')
        
        if not fabric_image_url:
            return Response(
                {"error": "fabric_image_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate analysis type
        valid_types = ['comprehensive', 'colors_only', 'texture_only']
        if analysis_type not in valid_types:
            return Response(
                {"error": f"analysis_type must be one of: {', '.join(valid_types)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check quota before processing
            if not self._check_quota(organization, 'fabric_analysis'):
                return Response(
                    {"error": "Monthly quota exceeded for fabric analysis"}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Perform fabric analysis
            analysis_result = self.fabric_analyzer.analyze_fabric(fabric_image_url, analysis_type)
            
            if not analysis_result['success']:
                return Response(
                    {"error": analysis_result.get('error', 'Fabric analysis failed')}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create AI generation request record
            with transaction.atomic():
                provider = self._get_or_create_provider('fabric_analysis')
                
                request_record = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=request.user,
                    provider=provider,
                    generation_type='fabric_analysis',
                    prompt=f"Fabric analysis for {fabric_image_url}",
                    parameters={
                        'fabric_image_url': fabric_image_url,
                        'analysis_type': analysis_type
                    },
                    result_data=analysis_result,
                    status='completed',
                    completed_at=timezone.now(),
                    cost=0.01  # Minimal cost for analysis
                )
                
                # Update quota
                self._update_quota(organization, provider, 'fabric_analysis', 0.01)
            
            # Add request ID to response
            analysis_result['request_id'] = str(request_record.id)
            analysis_result['cost'] = 0.01
            
            return Response(analysis_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Fabric analysis failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def extract_colors(self, request):
        """
        Extract color palette from fabric image
        POST /api/ai-services/fabric/extract-colors/
        
        Body:
        {
            "fabric_image_url": "https://example.com/fabric.jpg",
            "num_colors": 8  // Optional, default 8
        }
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_image_url = request.data.get('fabric_image_url')
        num_colors = request.data.get('num_colors', 8)
        
        if not fabric_image_url:
            return Response(
                {"error": "fabric_image_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate num_colors
        try:
            num_colors = int(num_colors)
            if num_colors < 1 or num_colors > 20:
                return Response(
                    {"error": "num_colors must be between 1 and 20"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {"error": "num_colors must be a valid integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check quota
            if not self._check_quota(organization, 'color_palette'):
                return Response(
                    {"error": "Monthly quota exceeded for color extraction"}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Extract color palette
            color_result = self.fabric_analyzer.extract_color_palette(fabric_image_url, num_colors)
            
            if not color_result['success']:
                return Response(
                    {"error": color_result.get('error', 'Color extraction failed')}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create AI generation request record
            with transaction.atomic():
                provider = self._get_or_create_provider('color_palette')
                
                request_record = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=request.user,
                    provider=provider,
                    generation_type='color_palette',
                    prompt=f"Color extraction for {fabric_image_url}",
                    parameters={
                        'fabric_image_url': fabric_image_url,
                        'num_colors': num_colors
                    },
                    result_data=color_result,
                    status='completed',
                    completed_at=timezone.now(),
                    cost=0.005  # Minimal cost for color extraction
                )
                
                # Update quota
                self._update_quota(organization, provider, 'color_palette', 0.005)
            
            # Add request ID to response
            color_result['request_id'] = str(request_record.id)
            color_result['cost'] = 0.005
            
            return Response(color_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Color extraction failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def analyze_texture(self, request):
        """
        Analyze fabric texture and patterns
        POST /api/ai-services/fabric/analyze-texture/
        
        Body:
        {
            "fabric_image_url": "https://example.com/fabric.jpg"
        }
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_image_url = request.data.get('fabric_image_url')
        
        if not fabric_image_url:
            return Response(
                {"error": "fabric_image_url is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check quota
            if not self._check_quota(organization, 'fabric_analysis'):
                return Response(
                    {"error": "Monthly quota exceeded for texture analysis"}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Analyze texture patterns
            texture_result = self.fabric_analyzer.analyze_texture_patterns(fabric_image_url)
            
            if not texture_result['success']:
                return Response(
                    {"error": texture_result.get('error', 'Texture analysis failed')}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Create AI generation request record
            with transaction.atomic():
                provider = self._get_or_create_provider('fabric_analysis')
                
                request_record = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=request.user,
                    provider=provider,
                    generation_type='fabric_analysis',
                    prompt=f"Texture analysis for {fabric_image_url}",
                    parameters={
                        'fabric_image_url': fabric_image_url,
                        'analysis_type': 'texture_only'
                    },
                    result_data=texture_result,
                    status='completed',
                    completed_at=timezone.now(),
                    cost=0.01
                )
                
                # Update quota
                self._update_quota(organization, provider, 'fabric_analysis', 0.01)
            
            # Add request ID to response
            texture_result['request_id'] = str(request_record.id)
            texture_result['cost'] = 0.01
            
            return Response(texture_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Texture analysis failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def match_colors(self, request):
        """
        Match colors between fabric and design
        POST /api/ai-services/fabric/match-colors/
        
        Body:
        {
            "fabric_colors": [
                {"hex": "#FF6B6B", "rgb": [255, 107, 107], "lab": [65, 45, 25], "percentage": 35},
                ...
            ],
            "design_colors": [
                {"hex": "#4ECDC4", "rgb": [78, 205, 196], "lab": [75, -25, -5], "percentage": 25},
                ...
            ]
        }
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_colors = request.data.get('fabric_colors', [])
        design_colors = request.data.get('design_colors', [])
        
        if not fabric_colors or not design_colors:
            return Response(
                {"error": "Both fabric_colors and design_colors are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check quota
            if not self._check_quota(organization, 'color_palette'):
                return Response(
                    {"error": "Monthly quota exceeded for color matching"}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Match colors using smart color matcher
            match_result = self.color_matcher.match_colors(fabric_colors, design_colors)
            
            # Create AI generation request record
            with transaction.atomic():
                provider = self._get_or_create_provider('color_palette')
                
                request_record = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=request.user,
                    provider=provider,
                    generation_type='color_palette',
                    prompt="Color matching between fabric and design",
                    parameters={
                        'fabric_colors_count': len(fabric_colors),
                        'design_colors_count': len(design_colors)
                    },
                    result_data=match_result,
                    status='completed',
                    completed_at=timezone.now(),
                    cost=0.002  # Minimal cost for color matching
                )
                
                # Update quota
                self._update_quota(organization, provider, 'color_palette', 0.002)
            
            # Add request ID to response
            match_result['request_id'] = str(request_record.id)
            match_result['cost'] = 0.002
            
            return Response(match_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Color matching failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def suggest_color_adjustments(self, request):
        """
        Suggest color adjustments for better harmony
        POST /api/ai-services/fabric/suggest-adjustments/
        
        Body:
        {
            "fabric_colors": [
                {"hex": "#FF6B6B", "rgb": [255, 107, 107], "lab": [65, 45, 25], "percentage": 35},
                ...
            ],
            "target_harmony": "complementary"  // "complementary", "analogous", "triadic", "split_complementary"
        }
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        fabric_colors = request.data.get('fabric_colors', [])
        target_harmony = request.data.get('target_harmony', 'complementary')
        
        if not fabric_colors:
            return Response(
                {"error": "fabric_colors is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate target harmony
        valid_harmonies = ['complementary', 'analogous', 'triadic', 'split_complementary']
        if target_harmony not in valid_harmonies:
            return Response(
                {"error": f"target_harmony must be one of: {', '.join(valid_harmonies)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Check quota
            if not self._check_quota(organization, 'color_palette'):
                return Response(
                    {"error": "Monthly quota exceeded for color suggestions"}, 
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Generate color adjustment suggestions
            suggestions = self.color_matcher.suggest_color_adjustments(fabric_colors, target_harmony)
            
            result = {
                'success': True,
                'fabric_colors': fabric_colors,
                'target_harmony': target_harmony,
                'suggestions': suggestions,
                'total_suggestions': len(suggestions)
            }
            
            # Create AI generation request record
            with transaction.atomic():
                provider = self._get_or_create_provider('color_palette')
                
                request_record = AIGenerationRequest.objects.create(
                    organization=organization,
                    user=request.user,
                    provider=provider,
                    generation_type='color_palette',
                    prompt=f"Color adjustment suggestions for {target_harmony} harmony",
                    parameters={
                        'fabric_colors_count': len(fabric_colors),
                        'target_harmony': target_harmony
                    },
                    result_data=result,
                    status='completed',
                    completed_at=timezone.now(),
                    cost=0.001  # Minimal cost for suggestions
                )
                
                # Update quota
                self._update_quota(organization, provider, 'color_palette', 0.001)
            
            # Add request ID to response
            result['request_id'] = str(request_record.id)
            result['cost'] = 0.001
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Color adjustment suggestions failed: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analysis_history(self, request):
        """
        Get fabric analysis history for the organization
        GET /api/ai-services/fabric/analysis-history/
        """
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get analysis requests
            analysis_requests = AIGenerationRequest.objects.filter(
                organization=organization,
                generation_type__in=['fabric_analysis', 'color_palette'],
                status='completed'
            ).order_by('-created_at')[:50]  # Last 50 analyses
            
            history = []
            for req in analysis_requests:
                history_item = {
                    'id': str(req.id),
                    'generation_type': req.generation_type,
                    'created_at': req.created_at.isoformat(),
                    'completed_at': req.completed_at.isoformat() if req.completed_at else None,
                    'cost': float(req.cost or 0),
                    'parameters': req.parameters,
                    'result_summary': self._get_result_summary(req.result_data)
                }
                history.append(history_item)
            
            return Response({
                'success': True,
                'total_analyses': len(history),
                'history': history
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Failed to get analysis history: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _check_quota(self, organization, generation_type: str) -> bool:
        """Check if organization has quota remaining"""
        try:
            quota = AIUsageQuota.objects.filter(
                organization=organization,
                generation_type=generation_type,
                quota_type='monthly'
            ).first()
            
            if not quota:
                return True  # No quota set, allow request
            
            return not quota.is_quota_exceeded()
            
        except Exception as e:
            logger.error(f"Failed to check quota: {str(e)}")
            return True  # Allow request if quota check fails
    
    def _update_quota(self, organization, provider, generation_type: str, cost: float):
        """Update usage quota"""
        try:
            quota, created = AIUsageQuota.objects.get_or_create(
                organization=organization,
                provider=provider,
                generation_type=generation_type,
                quota_type='monthly',
                defaults={
                    'max_requests': 1000,
                    'max_cost': 100.00,
                    'reset_at': timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=32)
                }
            )
            
            quota.increment_usage(cost=cost)
            
        except Exception as e:
            logger.error(f"Failed to update quota: {str(e)}")
    
    def _get_or_create_provider(self, provider_type: str) -> AIProvider:
        """Get or create AI provider"""
        provider_name = 'fabric_analysis' if provider_type == 'fabric_analysis' else 'color_palette'
        
        provider, created = AIProvider.objects.get_or_create(
            name=provider_name,
            defaults={
                'api_key': '',  # No external API needed for analysis
                'api_url': '',
                'is_active': True,
                'rate_limit_per_minute': 100,
                'rate_limit_per_hour': 1000
            }
        )
        
        return provider
    
    def _get_result_summary(self, result_data: dict) -> dict:
        """Get summary of analysis result"""
        if not result_data:
            return {}
        
        summary = {}
        
        if 'color_palette' in result_data:
            summary['colors_extracted'] = len(result_data['color_palette'])
            if result_data['color_palette']:
                summary['dominant_color'] = result_data['color_palette'][0].get('hex', 'Unknown')
        
        if 'texture_analysis' in result_data:
            texture = result_data['texture_analysis']
            summary['texture_type'] = texture.get('texture_type', 'Unknown')
            summary['fabric_type'] = texture.get('fabric_type', {}).get('predicted_type', 'Unknown')
        
        if 'quality_assessment' in result_data:
            quality = result_data['quality_assessment']
            summary['quality_grade'] = quality.get('quality_grade', 'Unknown')
        
        return summary

