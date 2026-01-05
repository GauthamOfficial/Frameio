"""
File upload views for AI services
Migrated to use Amazon S3 for file storage instead of local EC2 disk.
"""
import logging
import os
import uuid
from django.conf import settings
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone
from PIL import Image
import mimetypes
from io import BytesIO
from utils.s3_storage import upload_file_to_s3, generate_s3_key, file_exists_in_s3, delete_file_from_s3

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
        
        # Generate S3 key (path) for the file
        # Format: uploads/YYYY/MM/DD/uuid-filename.ext
        s3_key = generate_s3_key('uploads', unique_filename, date_prefix=True)
        
        # Read file content for S3 upload and image processing
        file_content = file.read()
        
        # Upload file to S3 (not local disk)
        file_url = upload_file_to_s3(
            file_content=file_content,
            s3_key=s3_key,
            content_type=file.content_type
        )
        
        # If it's an image, get dimensions from file content
        image_info = {}
        try:
            with Image.open(BytesIO(file_content)) as img:
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
                
                # Generate S3 key (path) for the file
                s3_key = generate_s3_key('uploads', unique_filename, date_prefix=True)
                
                # Read file content
                file_content = file.read()
                
                # Upload file to S3 (not local disk)
                file_url = upload_file_to_s3(
                    file_content=file_content,
                    s3_key=s3_key,
                    content_type=file.content_type
                )
                
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
        # Note: For S3, we need the full S3 key to check existence
        # Since we don't have the date prefix, we'll search common paths
        # In production, you might want to store the S3 key in the database
        # For now, we'll check a few common date patterns or use a simpler path
        
        # Try to find the file in S3 (check common upload paths)
        # Format: uploads/YYYY/MM/DD/filename
        possible_keys = [
            f"uploads/{timezone.now().strftime('%Y/%m/%d')}/{filename}",
            f"uploads/{filename}",  # Fallback without date prefix
        ]
        
        s3_key = None
        for key in possible_keys:
            if file_exists_in_s3(key):
                s3_key = key
                break
        
        if not s3_key:
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate S3 URL
        bucket_name = os.getenv('AWS_S3_BUCKET')
        region = os.getenv('AWS_REGION')
        file_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{s3_key}"
        
        # Note: Getting file size from S3 requires an additional API call
        # For now, we'll skip it or you can enhance this later
        file_size = None
        
        # Try to get image info (would require downloading from S3)
        # For now, we'll skip this to avoid additional S3 calls
        image_info = {}
        
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
        # Try to find the file in S3 (check common upload paths)
        possible_keys = [
            f"uploads/{timezone.now().strftime('%Y/%m/%d')}/{filename}",
            f"uploads/{filename}",  # Fallback without date prefix
        ]
        
        s3_key = None
        for key in possible_keys:
            if file_exists_in_s3(key):
                s3_key = key
                break
        
        if not s3_key:
            return Response(
                {"error": "File not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete file from S3
        deleted = delete_file_from_s3(s3_key)
        
        if not deleted:
            return Response(
                {"error": "Failed to delete file"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
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
