import os
import zipfile
import tempfile
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from typing import Dict, List, Optional, Any
import uuid
from PIL import Image
import io

from .models import ExportJob, ExportTemplate, ExportHistory
from designs.models import Design
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class DesignExportService:
    """Service for exporting designs in various formats"""
    
    def __init__(self):
        self.export_dir = os.path.join(settings.MEDIA_ROOT, 'exports')
        os.makedirs(self.export_dir, exist_ok=True)
    
    def create_export_job(
        self,
        user,
        design_ids: List[str],
        export_format: str,
        export_options: Dict[str, Any] = None,
        template_id: Optional[str] = None
    ) -> ExportJob:
        """
        Create a new export job
        
        Args:
            user: User creating the job
            design_ids: List of design IDs to export
            export_format: Export format (png, jpg, pdf, svg, zip)
            export_options: Additional export options
            template_id: Optional template ID to use
            
        Returns:
            Created ExportJob instance
        """
        organization = get_current_organization()
        if not organization:
            raise ValueError("No organization context available")
        
        # If template is provided, merge its parameters
        if template_id:
            try:
                template = ExportTemplate.objects.get(
                    id=template_id,
                    is_active=True,
                    organization=organization
                )
                # Merge template parameters with provided parameters
                export_format = template.export_format
                export_options = {**template.export_options, **(export_options or {})}
                
                # Increment template usage
                template.increment_usage()
                
            except ExportTemplate.DoesNotExist:
                logger.warning(f"Template {template_id} not found, using provided parameters")
        
        # Create the job
        job = ExportJob.objects.create(
            organization=organization,
            user=user,
            design_ids=design_ids,
            export_format=export_format,
            export_options=export_options or {}
        )
        
        logger.info(f"Created export job {job.id} for user {user.id}")
        return job
    
    def process_export_job(self, job: ExportJob) -> bool:
        """
        Process an export job
        
        Args:
            job: ExportJob instance to process
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Mark job as processing
            job.mark_processing()
            
            # Get designs
            designs = Design.objects.filter(
                id__in=job.design_ids,
                organization=job.organization
            )
            
            if not designs.exists():
                job.mark_failed("No valid designs found")
                return False
            
            # Process based on export format
            if job.export_format == 'zip':
                result = self._export_as_zip(job, designs)
            elif job.export_format in ['png', 'jpg']:
                result = self._export_as_images(job, designs)
            elif job.export_format == 'pdf':
                result = self._export_as_pdf(job, designs)
            elif job.export_format == 'svg':
                result = self._export_as_svg(job, designs)
            else:
                job.mark_failed(f"Unsupported export format: {job.export_format}")
                return False
            
            if result['success']:
                # Mark job as completed
                job.mark_completed(
                    export_file_path=result['file_path'],
                    download_url=result['download_url'],
                    file_size=result['file_size'],
                    processing_time=result['processing_time']
                )
                
                # Create history record
                ExportHistory.objects.create(
                    organization=job.organization,
                    user=job.user,
                    export_job=job
                )
                
                logger.info(f"Successfully processed export job {job.id}")
                return True
            else:
                # Mark job as failed
                job.mark_failed(result['error'])
                logger.error(f"Failed to process export job {job.id}: {result['error']}")
                return False
                
        except Exception as e:
            # Mark job as failed
            job.mark_failed(str(e))
            logger.error(f"Exception processing export job {job.id}: {str(e)}")
            return False
    
    def _export_as_zip(self, job: ExportJob, designs) -> Dict[str, Any]:
        """Export designs as a ZIP file"""
        import time
        start_time = time.time()
        
        try:
            # Create temporary ZIP file
            zip_filename = f"export_{job.id}.zip"
            zip_path = os.path.join(self.export_dir, zip_filename)
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for design in designs:
                    if design.image:
                        # Get image file
                        image_path = design.image.path
                        if os.path.exists(image_path):
                            # Add to ZIP with design title as filename
                            arcname = f"{design.title}_{design.id}.{job.export_format}"
                            zip_file.write(image_path, arcname)
                        else:
                            logger.warning(f"Image file not found for design {design.id}")
            
            # Get file size
            file_size = os.path.getsize(zip_path)
            
            # Generate download URL
            download_url = f"{settings.MEDIA_URL}exports/{zip_filename}"
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'file_path': zip_path,
                'download_url': download_url,
                'file_size': file_size,
                'processing_time': processing_time
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _export_as_images(self, job: ExportJob, designs) -> Dict[str, Any]:
        """Export designs as individual images"""
        import time
        start_time = time.time()
        
        try:
            # For single image export, return the first design
            if len(designs) == 1:
                design = designs.first()
                if design.image:
                    # Copy image to export directory
                    export_filename = f"export_{job.id}.{job.export_format}"
                    export_path = os.path.join(self.export_dir, export_filename)
                    
                    # Convert image format if needed
                    with Image.open(design.image.path) as img:
                        if job.export_format == 'jpg':
                            # Convert to RGB for JPEG
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')
                        img.save(export_path, format=job.export_format.upper())
                    
                    file_size = os.path.getsize(export_path)
                    download_url = f"{settings.MEDIA_URL}exports/{export_filename}"
                    
                    processing_time = time.time() - start_time
                    
                    return {
                        'success': True,
                        'file_path': export_path,
                        'download_url': download_url,
                        'file_size': file_size,
                        'processing_time': processing_time
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Design has no image',
                        'processing_time': time.time() - start_time
                    }
            else:
                # For multiple images, create a ZIP file
                return self._export_as_zip(job, designs)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _export_as_pdf(self, job: ExportJob, designs) -> Dict[str, Any]:
        """Export designs as PDF"""
        import time
        start_time = time.time()
        
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.utils import ImageReader
            
            # Create PDF file
            pdf_filename = f"export_{job.id}.pdf"
            pdf_path = os.path.join(self.export_dir, pdf_filename)
            
            # Get page size from options or use default
            page_size = job.export_options.get('page_size', 'A4')
            if page_size == 'A4':
                pagesize = A4
            else:
                pagesize = letter
            
            c = canvas.Canvas(pdf_path, pagesize=pagesize)
            
            for i, design in enumerate(designs):
                if design.image and os.path.exists(design.image.path):
                    # Add new page for each design (except first)
                    if i > 0:
                        c.showPage()
                    
                    # Get image dimensions
                    with Image.open(design.image.path) as img:
                        img_width, img_height = img.size
                    
                    # Calculate scaling to fit page
                    page_width, page_height = pagesize
                    margin = 50
                    available_width = page_width - (2 * margin)
                    available_height = page_height - (2 * margin)
                    
                    scale_x = available_width / img_width
                    scale_y = available_height / img_height
                    scale = min(scale_x, scale_y)
                    
                    new_width = img_width * scale
                    new_height = img_height * scale
                    
                    # Center image on page
                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2
                    
                    # Add image to PDF
                    c.drawImage(
                        design.image.path,
                        x, y,
                        width=new_width,
                        height=new_height
                    )
                    
                    # Add design title
                    c.setFont("Helvetica", 12)
                    c.drawString(margin, page_height - 30, f"Design: {design.title}")
            
            c.save()
            
            file_size = os.path.getsize(pdf_path)
            download_url = f"{settings.MEDIA_URL}exports/{pdf_filename}"
            
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'file_path': pdf_path,
                'download_url': download_url,
                'file_size': file_size,
                'processing_time': processing_time
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'PDF export requires reportlab library',
                'processing_time': time.time() - start_time
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def _export_as_svg(self, job: ExportJob, designs) -> Dict[str, Any]:
        """Export designs as SVG"""
        import time
        start_time = time.time()
        
        try:
            # For now, convert images to SVG (basic implementation)
            if len(designs) == 1:
                design = designs.first()
                if design.image:
                    # Create basic SVG with embedded image
                    export_filename = f"export_{job.id}.svg"
                    export_path = os.path.join(self.export_dir, export_filename)
                    
                    # Get image dimensions
                    with Image.open(design.image.path) as img:
                        width, height = img.size
                    
                    # Create SVG content
                    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <image href="{design.image.url}" width="{width}" height="{height}"/>
</svg>'''
                    
                    with open(export_path, 'w') as f:
                        f.write(svg_content)
                    
                    file_size = os.path.getsize(export_path)
                    download_url = f"{settings.MEDIA_URL}exports/{export_filename}"
                    
                    processing_time = time.time() - start_time
                    
                    return {
                        'success': True,
                        'file_path': export_path,
                        'download_url': download_url,
                        'file_size': file_size,
                        'processing_time': processing_time
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Design has no image',
                        'processing_time': time.time() - start_time
                    }
            else:
                # For multiple designs, create a ZIP file
                return self._export_as_zip(job, designs)
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': time.time() - start_time
            }
    
    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get status of an export job
        
        Args:
            job_id: Job ID
            
        Returns:
            Dict containing job status information
        """
        try:
            job = ExportJob.objects.get(id=job_id)
            
            status_info = {
                'job_id': str(job.id),
                'status': job.status,
                'progress': self._calculate_progress(job),
                'message': self._get_status_message(job),
                'created_at': job.created_at,
                'updated_at': job.updated_at
            }
            
            if job.status == 'completed':
                status_info['download_url'] = job.download_url
                status_info['file_size'] = job.file_size
                status_info['expires_at'] = job.expires_at
                status_info['processing_time'] = job.processing_time
            elif job.status == 'failed':
                status_info['error_message'] = job.error_message
            
            return status_info
            
        except ExportJob.DoesNotExist:
            return {
                'job_id': job_id,
                'status': 'not_found',
                'progress': 0,
                'message': 'Job not found',
                'error_message': 'The specified job ID does not exist'
            }
    
    def _calculate_progress(self, job: ExportJob) -> int:
        """Calculate progress percentage for a job"""
        if job.status == 'pending':
            return 10
        elif job.status == 'processing':
            return 50
        elif job.status == 'completed':
            return 100
        elif job.status == 'failed':
            return 0
        elif job.status == 'cancelled':
            return 0
        return 0
    
    def _get_status_message(self, job: ExportJob) -> str:
        """Get human-readable status message for a job"""
        if job.status == 'pending':
            return 'Export job is queued for processing'
        elif job.status == 'processing':
            return 'Processing export...'
        elif job.status == 'completed':
            return 'Export completed successfully'
        elif job.status == 'failed':
            return 'Export failed'
        elif job.status == 'cancelled':
            return 'Export was cancelled'
        return 'Unknown status'
    
    def cleanup_expired_exports(self):
        """Clean up expired export files"""
        try:
            expired_jobs = ExportJob.objects.filter(
                status='completed',
                expires_at__lt=timezone.now()
            )
            
            for job in expired_jobs:
                if job.export_file_path and os.path.exists(job.export_file_path):
                    try:
                        os.remove(job.export_file_path)
                        logger.info(f"Cleaned up expired export file: {job.export_file_path}")
                    except OSError as e:
                        logger.error(f"Failed to clean up export file {job.export_file_path}: {e}")
            
            logger.info(f"Cleaned up {expired_jobs.count()} expired export files")
            
        except Exception as e:
            logger.error(f"Error cleaning up expired exports: {e}")
