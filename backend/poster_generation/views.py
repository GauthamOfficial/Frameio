from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Sum
from django.core.cache import cache
import logging

from .models import PosterGenerationJob, PosterTemplate, PosterGenerationHistory
from .serializers import (
    PosterGenerationJobSerializer, PosterGenerationJobCreateSerializer,
    PosterTemplateSerializer, PosterTemplatePublicSerializer,
    PosterGenerationHistorySerializer, PosterGenerationStatusSerializer,
    PosterGenerationRequestSerializer
)
from .services import PosterGenerationService
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class PosterGenerationJobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing poster generation jobs"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return PosterGenerationJobCreateSerializer
        return PosterGenerationJobSerializer
    
    def get_queryset(self):
        """Return jobs for current organization and user"""
        organization = get_current_organization()
        if not organization:
            return PosterGenerationJob.objects.none()
        
        queryset = PosterGenerationJob.objects.filter(organization=organization)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.select_related('user', 'organization').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new poster generation job"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Create the job
        job = serializer.save(
            organization=organization,
            user=self.request.user
        )
        
        # Process the job asynchronously
        try:
            service = PosterGenerationService()
            service.process_generation_job(job)
        except Exception as e:
            logger.error(f"Failed to process poster generation job {job.id}: {str(e)}")
            job.mark_failed(str(e))
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a poster generation job"""
        try:
            service = PosterGenerationService()
            success = service.cancel_job(pk, request.user)
            
            if success:
                return Response(
                    {'message': 'Job cancelled successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Job could not be cancelled'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            logger.error(f"Error cancelling job {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get status of a poster generation job"""
        try:
            service = PosterGenerationService()
            status_info = service.get_job_status(pk)
            
            serializer = PosterGenerationStatusSerializer(status_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting job status {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PosterTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing poster templates"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list' and self.request.query_params.get('public'):
            return PosterTemplatePublicSerializer
        return PosterTemplateSerializer
    
    def get_queryset(self):
        """Return templates for current organization and public templates"""
        organization = get_current_organization()
        if not organization:
            return PosterTemplate.objects.none()
        
        queryset = PosterTemplate.objects.filter(
            Q(organization=organization) | Q(is_public=True, is_active=True)
        )
        
        # Filter by category if provided
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by public only if requested
        if self.request.query_params.get('public'):
            queryset = queryset.filter(is_public=True, is_active=True)
        
        return queryset.select_related('created_by', 'organization').order_by('-usage_count', 'name')
    
    def perform_create(self, serializer):
        """Create template with current organization"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        serializer.save(
            organization=organization,
            created_by=self.request.user
        )
    
    @action(detail=True, methods=['post'])
    def use_template(self, request, pk=None):
        """Use a template for poster generation"""
        try:
            template = self.get_object()
            
            # Create generation request using template
            request_serializer = PosterGenerationRequestSerializer(
                data=request.data,
                context={'organization': get_current_organization()}
            )
            
            if request_serializer.is_valid():
                # Create generation job
                service = PosterGenerationService()
                job = service.create_generation_job(
                    user=request.user,
                    prompt=request_serializer.validated_data['prompt'],
                    negative_prompt=request_serializer.validated_data.get('negative_prompt', ''),
                    design_metadata=request_serializer.validated_data.get('design_metadata', {}),
                    width=request_serializer.validated_data.get('width', 1024),
                    height=request_serializer.validated_data.get('height', 1024),
                    num_images=request_serializer.validated_data.get('num_images', 1),
                    guidance_scale=request_serializer.validated_data.get('guidance_scale', 7.5),
                    num_inference_steps=request_serializer.validated_data.get('num_inference_steps', 20),
                    template_id=str(template.id)
                )
                
                # Process the job
                service.process_generation_job(job)
                
                return Response(
                    {
                        'message': 'Poster generation started',
                        'job_id': str(job.id),
                        'status': job.status
                    },
                    status=status.HTTP_201_CREATED
                )
            else:
                return Response(
                    request_serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error using template {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PosterGenerationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing poster generation history"""
    
    serializer_class = PosterGenerationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return history for current organization and user"""
        organization = get_current_organization()
        if not organization:
            return PosterGenerationHistory.objects.none()
        
        queryset = PosterGenerationHistory.objects.filter(organization=organization)
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.select_related('user', 'job').order_by('-created_at')


class PosterGenerationAPIView(viewsets.ViewSet):
    """Main API view for poster generation"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = PosterGenerationService()
    
    @action(detail=False, methods=['post'])
    def generate_poster(self, request):
        """Generate poster with AI"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = PosterGenerationRequestSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create generation job
            job = self.service.create_generation_job(
                user=request.user,
                prompt=serializer.validated_data['prompt'],
                negative_prompt=serializer.validated_data.get('negative_prompt', ''),
                design_metadata=serializer.validated_data.get('design_metadata', {}),
                width=serializer.validated_data.get('width', 1024),
                height=serializer.validated_data.get('height', 1024),
                num_images=serializer.validated_data.get('num_images', 1),
                guidance_scale=serializer.validated_data.get('guidance_scale', 7.5),
                num_inference_steps=serializer.validated_data.get('num_inference_steps', 20),
                template_id=serializer.validated_data.get('template_id')
            )
            
            # Process the job
            self.service.process_generation_job(job)
            
            return Response(
                {
                    'success': True,
                    'message': 'Poster generation started',
                    'job_id': str(job.id),
                    'status': job.status,
                    'estimated_completion': None  # Could be calculated based on queue
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Poster generation failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def job_status(self, request):
        """Get status of a poster generation job"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {"error": "job_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            status_info = self.service.get_job_status(job_id)
            serializer = PosterGenerationStatusSerializer(status_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting job status {job_id}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available poster templates"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get templates for organization and public templates
            templates = PosterTemplate.objects.filter(
                Q(organization=organization) | Q(is_public=True, is_active=True)
            ).select_related('created_by', 'organization')
            
            # Filter by category if provided
            category = request.query_params.get('category')
            if category:
                templates = templates.filter(category=category)
            
            serializer = PosterTemplatePublicSerializer(templates, many=True)
            
            return Response(
                {
                    'success': True,
                    'templates': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to get poster templates: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get poster generation analytics"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get analytics data
            total_jobs = PosterGenerationJob.objects.filter(organization=organization).count()
            completed_jobs = PosterGenerationJob.objects.filter(
                organization=organization,
                status='completed'
            ).count()
            failed_jobs = PosterGenerationJob.objects.filter(
                organization=organization,
                status='failed'
            ).count()
            
            # Calculate success rate
            success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Get average processing time
            avg_processing_time = PosterGenerationJob.objects.filter(
                organization=organization,
                status='completed',
                processing_time__isnull=False
            ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0
            
            # Get total cost
            total_cost = PosterGenerationJob.objects.filter(
                organization=organization,
                status='completed',
                cost__isnull=False
            ).aggregate(total_cost=Sum('cost'))['total_cost'] or 0
            
            analytics_data = {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'success_rate': round(success_rate, 2),
                'average_processing_time': round(avg_processing_time, 2),
                'total_cost': float(total_cost)
            }
            
            return Response(
                {
                    'success': True,
                    'analytics': analytics_data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to get analytics: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )