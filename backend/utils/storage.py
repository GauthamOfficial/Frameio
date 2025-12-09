"""
Dual-mode storage helper for image uploads.
Supports Cloudinary (dev) and local media storage (prod) based on USE_CLOUDINARY env var.
"""
import os
import logging
import uuid
from typing import Optional
from io import BytesIO
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# Try to import Cloudinary
try:
    import cloudinary
    import cloudinary.uploader
    CLOUDINARY_AVAILABLE = True
except ImportError:
    CLOUDINARY_AVAILABLE = False
    logger.warning("Cloudinary package not installed. Cloudinary mode will not work.")


def upload_image_bytes(image_bytes: bytes, filename: Optional[str] = None, request=None) -> str:
    """
    Upload image bytes using the configured storage mode.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        request: Django request object for building absolute URLs (required for local mode)
    
    Returns:
        Public URL of the uploaded image (Cloudinary URL or local media URL)
    
    Raises:
        ValueError: If local mode is used without request object
        Exception: If upload fails
    """
    use_cloudinary = os.getenv('USE_CLOUDINARY', 'True').lower() == 'true'
    
    if use_cloudinary:
        return _upload_to_cloudinary(image_bytes, filename)
    else:
        if request is None:
            raise ValueError("request object is required for local storage mode to build absolute URLs")
        return _upload_to_local(image_bytes, filename, request)


def _upload_to_cloudinary(image_bytes: bytes, filename: Optional[str] = None) -> str:
    """
    Upload image bytes to Cloudinary and return secure URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename
    
    Returns:
        Cloudinary secure URL
    
    Raises:
        ValueError: If Cloudinary is not configured or unavailable
        Exception: If upload fails
    """
    if not CLOUDINARY_AVAILABLE:
        raise ValueError("Cloudinary package not installed. Install with: pip install cloudinary")
    
    # Get Cloudinary credentials
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        raise ValueError(
            "Cloudinary credentials not configured. Please set CLOUDINARY_CLOUD_NAME, "
            "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables."
        )
    
    # Configure Cloudinary
    try:
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret
        )
    except Exception as e:
        logger.error(f"Failed to configure Cloudinary: {e}")
        raise
    
    # Generate filename if not provided
    if not filename:
        filename = f"{uuid.uuid4().hex}.png"
    
    try:
        # Upload bytes directly to Cloudinary
        result = cloudinary.uploader.upload(
            image_bytes,
            folder="generated",
            resource_type="image",
            format="png",
            public_id=filename.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        )
        
        public_url = result.get('secure_url') or result.get('url')
        if not public_url:
            raise ValueError("Cloudinary upload succeeded but no URL returned")
        
        logger.info(f"Successfully uploaded to Cloudinary: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to upload to Cloudinary: {str(e)}")
        raise


def _upload_to_local(image_bytes: bytes, filename: Optional[str] = None, request=None) -> str:
    """
    Save image bytes to local media storage and return absolute URL.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate UUID-based name if not provided)
        request: Django request object for building absolute URLs
    
    Returns:
        Absolute URL to the local media file
    
    Raises:
        ValueError: If request is None
        Exception: If save fails
    """
    if request is None:
        raise ValueError("request object is required for local storage mode")
    
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
        
        # Build absolute URL using request
        relative_url = default_storage.url(saved_path)
        # Remove leading slash if present (build_absolute_uri adds it)
        if relative_url.startswith('/'):
            relative_url = relative_url[1:]
        
        absolute_url = request.build_absolute_uri(relative_url)
        logger.info(f"Local storage URL: {absolute_url}")
        
        return absolute_url
        
    except Exception as e:
        logger.error(f"Failed to save image locally: {str(e)}")
        raise


def delete_local_file(storage_path: str) -> bool:
    """
    Delete a local file from storage (useful after Cloudinary upload).
    
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



