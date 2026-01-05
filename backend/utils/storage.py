"""
Storage helper for image uploads.
Migrated to use Amazon S3 for file storage instead of local EC2 disk.
"""
import os
import logging
import uuid
from typing import Optional
from django.conf import settings
from utils.s3_storage import upload_file_to_s3, generate_s3_key, delete_file_from_s3

logger = logging.getLogger(__name__)


def upload_image_bytes(image_bytes: bytes, filename: Optional[str] = None, request=None) -> str:
    """
    Upload image bytes to S3 and return public URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        request: Django request object (optional, kept for API compatibility)
    
    Returns:
        Public S3 URL of the uploaded image
    
    Raises:
        Exception: If upload fails
    """
    return _upload_to_s3(image_bytes, filename)


def _upload_to_s3(image_bytes: bytes, filename: Optional[str] = None) -> str:
    """
    Upload image bytes to S3 and return public URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
    
    Returns:
        Public S3 URL of the uploaded image
    
    Raises:
        Exception: If upload fails
    """
    # Generate filename if not provided
    if not filename:
        filename = f"{uuid.uuid4().hex}.png"
    
    # Generate S3 key (path) for the file
    # Store in 'generated' folder with date prefix
    s3_key = generate_s3_key('generated', filename, date_prefix=True)
    
    try:
        # Upload to S3 (not local disk)
        # Determine content type from filename extension
        content_type = 'image/png'  # Default
        if filename.lower().endswith('.jpg') or filename.lower().endswith('.jpeg'):
            content_type = 'image/jpeg'
        elif filename.lower().endswith('.webp'):
            content_type = 'image/webp'
        
        public_url = upload_file_to_s3(
            file_content=image_bytes,
            s3_key=s3_key,
            content_type=content_type
        )
        
        logger.info(f"Image uploaded to S3: {s3_key} -> {public_url}")
        
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to upload image to S3: {str(e)}")
        raise


def delete_local_file(storage_path: str) -> bool:
    """
    Delete a file from S3 storage.
    Note: Function name kept for backward compatibility, but now deletes from S3.
    
    Args:
        storage_path: S3 key (path) to delete (e.g., 'generated/2024/01/15/filename.png')
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        # Delete from S3
        deleted = delete_file_from_s3(storage_path)
        
        if deleted:
            logger.info(f"Deleted file from S3: {storage_path}")
        else:
            logger.warning(f"File not found or failed to delete from S3: {storage_path}")
        
        return deleted
    except Exception as e:
        logger.error(f"Failed to delete file from S3 {storage_path}: {str(e)}")
        return False
