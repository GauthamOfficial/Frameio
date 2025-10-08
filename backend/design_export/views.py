from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Avg, Sum
from django.core.cache import cache
from django.http import HttpResponse, Http404
import logging
import os

from .models import ExportJob, ExportTemplate, ExportHistory
from .serializers import (
    ExportJobSerializer, ExportJobCreateSerializer,
    ExportTemplateSerializer, ExportTemplatePublicSerializer,
    ExportHistorySerializer, ExportRequestSerializer,
    ExportStatusSerializer, DownloadRequestSerializer
)
from .services import DesignExportService
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class ExportJobViewSet(viewsets.ModelViewSet):
    """ViewSet for managing export jobs"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return ExportJobCreateSerializer
        return ExportJobSerializer
    
    def get_queryset(self):
        """Return jobs for current organization and user"""
        organization = get_current_organization()
        if not organization:
            return ExportJob.objects.none()
        
        queryset = ExportJob.objects.filter(organization=organization)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.select_related('user', 'organization').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new export job"""
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # Create the job
        job = serializer.save(
            organization=organization,
            user=self.request.user
        )
        
        # Process the job
        try:
            service = DesignExportService()
            service.process_export_job(job)
        except Exception as e:
            logger.error(f"Failed to process export job {job.id}: {str(e)}")
            job.mark_failed(str(e))
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an export job"""
        try:
            job = self.get_object()
            
            if job.status in ['pending', 'processing']:
                job.cancel()
                return Response(
                    {'message': 'Job cancelled successfully'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'error': 'Job cannot be cancelled'},
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
        """Get status of an export job"""
        try:
            service = DesignExportService()
            status_info = service.get_job_status(pk)
            
            serializer = ExportStatusSerializer(status_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting job status {pk}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing export templates"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list' and self.request.query_params.get('public'):
            return ExportTemplatePublicSerializer
        return ExportTemplateSerializer
    
    def get_queryset(self):
        """Return templates for current organization and public templates"""
        organization = get_current_organization()
        if not organization:
            return ExportTemplate.objects.none()
        
        queryset = ExportTemplate.objects.filter(
            Q(organization=organization) | Q(is_public=True, is_active=True)
        )
        
        # Filter by template type if provided
        template_type = self.request.query_params.get('template_type')
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        
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
        """Use a template for export"""
        try:
            template = self.get_object()
            
            # Create export request using template
            request_serializer = ExportRequestSerializer(
                data=request.data,
                context={'organization': get_current_organization()}
            )
            
            if request_serializer.is_valid():
                # Create export job
                service = DesignExportService()
                job = service.create_export_job(
                    user=request.user,
                    design_ids=request_serializer.validated_data['design_ids'],
                    export_format=request_serializer.validated_data.get('export_format', template.export_format),
                    export_options=request_serializer.validated_data.get('export_options', {}),
                    template_id=str(template.id)
                )
                
                # Process the job
                service.process_export_job(job)
                
                return Response(
                    {
                        'message': 'Export started',
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


class ExportHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing export history"""
    
    serializer_class = ExportHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return history for current organization and user"""
        organization = get_current_organization()
        if not organization:
            return ExportHistory.objects.none()
        
        queryset = ExportHistory.objects.filter(organization=organization)
        
        # Filter by user if not admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset.select_related('user', 'export_job').order_by('-created_at')


class ExportAPIView(viewsets.ViewSet):
    """Main API view for design export"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = DesignExportService()
    
    @action(detail=False, methods=['post'])
    def export_designs(self, request):
        """Export designs in specified format"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = ExportRequestSerializer(
            data=request.data,
            context={'organization': organization}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Create export job
            job = self.service.create_export_job(
                user=request.user,
                design_ids=serializer.validated_data['design_ids'],
                export_format=serializer.validated_data['export_format'],
                export_options=serializer.validated_data.get('export_options', {}),
                template_id=serializer.validated_data.get('template_id')
            )
            
            # Process the job
            self.service.process_export_job(job)
            
            return Response(
                {
                    'success': True,
                    'message': 'Export started',
                    'job_id': str(job.id),
                    'status': job.status
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Design export failed: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def job_status(self, request):
        """Get status of an export job"""
        job_id = request.query_params.get('job_id')
        if not job_id:
            return Response(
                {"error": "job_id parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            status_info = self.service.get_job_status(job_id)
            serializer = ExportStatusSerializer(status_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting job status {job_id}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def download(self, request):
        """Download exported file"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate request data
        serializer = DownloadRequestSerializer(
            data=request.data,
            context={'organization': organization, 'user': request.user}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job_id = serializer.validated_data['job_id']
            job = ExportJob.objects.get(id=job_id)
            
            # Increment download count in history
            if hasattr(job, 'history'):
                job.history.increment_download_count()
            
            # Return download URL
            return Response(
                {
                    'success': True,
                    'download_url': job.download_url,
                    'file_size': job.file_size,
                    'expires_at': job.expires_at
                },
                status=status.HTTP_200_OK
            )
            
        except ExportJob.DoesNotExist:
            return Response(
                {"error": "Export job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error downloading export {job_id}: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available export templates"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get templates for organization and public templates
            templates = ExportTemplate.objects.filter(
                Q(organization=organization) | Q(is_public=True, is_active=True)
            ).select_related('created_by', 'organization')
            
            # Filter by template type if provided
            template_type = request.query_params.get('template_type')
            if template_type:
                templates = templates.filter(template_type=template_type)
            
            serializer = ExportTemplatePublicSerializer(templates, many=True)
            
            return Response(
                {
                    'success': True,
                    'templates': serializer.data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Failed to get export templates: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get export analytics"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get analytics data
            total_jobs = ExportJob.objects.filter(organization=organization).count()
            completed_jobs = ExportJob.objects.filter(
                organization=organization,
                status='completed'
            ).count()
            failed_jobs = ExportJob.objects.filter(
                organization=organization,
                status='failed'
            ).count()
            
            # Calculate success rate
            success_rate = (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            
            # Get average processing time
            avg_processing_time = ExportJob.objects.filter(
                organization=organization,
                status='completed',
                processing_time__isnull=False
            ).aggregate(avg_time=Avg('processing_time'))['avg_time'] or 0
            
            # Get total file size
            total_file_size = ExportJob.objects.filter(
                organization=organization,
                status='completed',
                file_size__isnull=False
            ).aggregate(total_size=Sum('file_size'))['total_size'] or 0
            
            analytics_data = {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'failed_jobs': failed_jobs,
                'success_rate': round(success_rate, 2),
                'average_processing_time': round(avg_processing_time, 2),
                'total_file_size': total_file_size
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
    
    @action(detail=False, methods=['post'])
    def cleanup(self, request):
        """Clean up expired export files (admin only)"""
        if not request.user.is_staff:
            return Response(
                {"error": "Admin access required"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            self.service.cleanup_expired_exports()
            return Response(
                {'message': 'Cleanup completed successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )