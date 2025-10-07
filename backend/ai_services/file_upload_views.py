"""
File upload views for AI services
"""
import logging
import os
import uuid
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from PIL import Image
import mimetypes

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_file(request):
    """
    Upload file endpoint
    POST /api/upload/
    """
    try:
        if 'file' not in request.FILES:
            return Response(
                {"error": "No file provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file = request.FILES['file']
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            return Response(
                {"error": f"File type {file.content_type} not supported. Allowed types: {', '.join(allowed_types)}"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate file size (10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            return Response(
                {"error": f"File too large. Maximum size is {max_size // (1024*1024)}MB"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate unique filename
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create upload path
        upload_path = f"uploads/{timezone.now().strftime('%Y/%m/%d')}/{unique_filename}"
        
        # Save file
        saved_path = default_storage.save(upload_path, file)
        
        # Get file URL
        file_url = default_storage.url(saved_path)
        
        # If it's an image, get dimensions
        image_info = {}
        try:
            with default_storage.open(saved_path, 'rb') as f:
                with Image.open(f) as img:
                    image_info = {
                        'width': img.width,
                        'height': img.height,
                        'format': img.format
                    }
        except Exception as e:
            logger.warning(f"Could not get image info: {str(e)}")
        
        return Response({
            'success': True,
            'url': file_url,
            'filename': unique_filename,
            'original_name': file.name,
            'size': file.size,
            'content_type': file.content_type,
            'uploaded_at': timezone.now().isoformat(),
            'image_info': image_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        return Response(
            {"error": f"File upload failed: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_multiple_files(request):
    """
    Upload multiple files endpoint
    POST /api/upload/multiple/
    """
    try:
        if 'files' not in request.FILES:
            return Response(
                {"error": "No files provided"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        files = request.FILES.getlist('files')
        uploaded_files = []
        errors = []
        
        for i, file in enumerate(files):
            try:
                # Validate file type
                allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
                if file.content_type not in allowed_types:
                    errors.append(f"File {i+1} ({file.name}): Unsupported file type")
                    continue
                
                # Validate file size (10MB limit)
                max_size = 10 * 1024 * 1024  # 10MB
                if file.size > max_size:
                    errors.append(f"File {i+1} ({file.name}): File too large")
                    continue
                
                # Generate unique filename
                file_extension = os.path.splitext(file.name)[1]
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                
                # Create upload path
                upload_path = f"uploads/{timezone.now().strftime('%Y/%m/%d')}/{unique_filename}"
                
                # Save file
                saved_path = default_storage.save(upload_path, file)
                
                # Get file URL
                file_url = default_storage.url(saved_path)
                
                uploaded_files.append({
                    'url': file_url,
                    'filename': unique_filename,
                    'original_name': file.name,
                    'size': file.size,
                    'content_type': file.content_type
                })
                
            except Exception as e:
                errors.append(f"File {i+1} ({file.name}): {str(e)}")
        
        return Response({
            'success': len(uploaded_files) > 0,
            'uploaded_files': uploaded_files,
            'errors': errors,
            'total_uploaded': len(uploaded_files),
            'total_errors': len(errors)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Multiple file upload failed: {str(e)}")
        return Response(
            {"error": f"Multiple file upload failed: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_file_info(request, filename):
    """
    Get file information
    GET /api/upload/info/{filename}/
    """
    try:
        # Find file in storage
        upload_path = f"uploads/{filename}"
        
        if not default_storage.exists(upload_path):
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get file info
        file_size = default_storage.size(upload_path)
        file_url = default_storage.url(upload_path)
        
        # Try to get image info
        image_info = {}
        try:
            with default_storage.open(upload_path, 'rb') as f:
                with Image.open(f) as img:
                    image_info = {
                        'width': img.width,
                        'height': img.height,
                        'format': img.format
                    }
        except Exception as e:
            logger.warning(f"Could not get image info: {str(e)}")
        
        return Response({
            'success': True,
            'filename': filename,
            'url': file_url,
            'size': file_size,
            'image_info': image_info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get file info failed: {str(e)}")
        return Response(
            {"error": f"Get file info failed: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_file(request, filename):
    """
    Delete file
    DELETE /api/upload/{filename}/
    """
    try:
        # Find file in storage
        upload_path = f"uploads/{filename}"
        
        if not default_storage.exists(upload_path):
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete file
        default_storage.delete(upload_path)
        
        return Response({
            'success': True,
            'message': f'File {filename} deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Delete file failed: {str(e)}")
        return Response(
            {"error": f"Delete file failed: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
