"""
Local storage helper for image uploads.
Uses local media storage with public URLs based on DOMAIN_URL.
"""
import os
import logging
import uuid
from typing import Optional
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)


def upload_image_bytes(image_bytes: bytes, filename: Optional[str] = None, request=None) -> str:
    """
    Upload image bytes to local storage and return public URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        request: Django request object for building absolute URLs (optional, will use DOMAIN_URL if not provided)
    
    Returns:
        Public URL of the uploaded image
    
    Raises:
        Exception: If upload fails
    """
    return _upload_to_local(image_bytes, filename, request)


def _upload_to_local(image_bytes: bytes, filename: Optional[str] = None, request=None) -> str:
    """
    Save image bytes to local media storage and return absolute URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        request: Django request object for building absolute URLs (optional)
    
    Returns:
        Absolute URL to the local media file
    
    Raises:
        Exception: If save fails
    """
    # Generate filename if not provided
    if not filename:
        filename = f"{uuid.uuid4().hex}.png"
    
    # Ensure generated/ directory exists in MEDIA_ROOT
    media_root = settings.MEDIA_ROOT
    generated_dir = media_root / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    
    # Save to Django storage
    storage_path = f"generated/{filename}"
    
    try:
        saved_path = default_storage.save(storage_path, ContentFile(image_bytes))
        logger.info(f"Image saved locally to: {saved_path}")
        
        # Build absolute URL
        relative_url = default_storage.url(saved_path)
        
        # Remove leading slash if present
        if relative_url.startswith('/'):
            relative_url = relative_url[1:]
        
        # Use request to build absolute URL if available
        if request:
            absolute_url = request.build_absolute_uri(relative_url)
        else:
            # Use DOMAIN_URL from settings or environment
            domain_url = getattr(settings, 'DOMAIN_URL', '') or os.getenv('DOMAIN_URL', '')
            if domain_url:
                domain_url = domain_url.rstrip('/')
                absolute_url = f"{domain_url}/{relative_url}"
            else:
                # Fallback to localhost in development
                absolute_url = f"http://localhost:8000/{relative_url}"
        
        logger.info(f"Local storage URL: {absolute_url}")
        
        return absolute_url
        
    except Exception as e:
        logger.error(f"Failed to save image locally: {str(e)}")
        raise


def delete_local_file(storage_path: str) -> bool:
    """
    Delete a local file from storage.
    
    Args:
        storage_path: Django storage path to delete
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if default_storage.exists(storage_path):
            default_storage.delete(storage_path)
            logger.info(f"Deleted local file: {storage_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {storage_path}")
            return False
    except Exception as e:
        logger.error(f"Failed to delete local file {storage_path}: {str(e)}")
        return False
