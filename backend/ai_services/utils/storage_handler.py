"""
Dual-mode storage handler for poster images.
Supports both Cloudinary (development) and local server storage (production).
"""
import os
import logging
import time
import uuid
from typing import Optional
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO

logger = logging.getLogger(__name__)

# Import Cloudinary utilities
from .cloudinary_utils import upload_to_cloudinary, upload_html_to_cloudinary, create_shareable_html_page


def get_storage_mode() -> str:
    """
    Get the current storage mode from environment variable.
    
    Returns:
        'cloudinary' if USE_CLOUDINARY=True, 'local' otherwise
    """
    use_cloudinary = os.getenv('USE_CLOUDINARY', 'True').lower() == 'true'
    return 'cloudinary' if use_cloudinary else 'local'


def get_domain_url() -> str:
    """
    Get the domain URL for local storage mode.
    Falls back to localhost in development.
    
    Returns:
        Domain URL (e.g., https://example.com or http://localhost:8000)
    """
    # Try to get from settings first (set via env var)
    domain = getattr(settings, 'DOMAIN_URL', '')
    if not domain:
        domain = os.getenv('DOMAIN_URL', '')
    
    if domain:
        return domain.rstrip('/')
    
    # Fallback to localhost in development
    if settings.DEBUG:
        return 'http://localhost:8000'
    
    # Production fallback - should be set via env var
    logger.warning("DOMAIN_URL not set, using localhost fallback")
    return 'http://localhost:8000'


def save_poster_image(image_bytes: bytes, filename: str = None) -> tuple[str, str]:
    """
    Save poster image to local storage.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate if not provided)
    
    Returns:
        Tuple of (saved_path, image_url)
    """
    if not filename:
        filename = f"poster_{uuid.uuid4().hex[:8]}_{int(time.time())}.png"
    
    # Ensure generated/ directory exists
    output_path = f"generated/{filename}"
    
    # Save to media storage
    saved_path = default_storage.save(output_path, ContentFile(image_bytes))
    image_url = default_storage.url(saved_path)
    
    # Ensure full URL for sharing
    if not image_url.startswith('http'):
        domain = get_domain_url()
        image_url = f"{domain}{image_url}"
    
    return saved_path, image_url


def upload_poster_image(image_path: str) -> Optional[str]:
    """
    Upload poster image using the configured storage mode.
    
    Args:
        image_path: Path to the image file (Django storage path)
    
    Returns:
        Public URL of the uploaded image, or None if upload fails
    """
    storage_mode = get_storage_mode()
    
    if storage_mode == 'cloudinary':
        logger.info(f"Using Cloudinary storage mode for: {image_path}")
        return upload_to_cloudinary(image_path)
    else:
        logger.info(f"Using local storage mode for: {image_path}")
        # For local storage, return the media URL
        if default_storage.exists(image_path):
            image_url = default_storage.url(image_path)
            if not image_url.startswith('http'):
                domain = get_domain_url()
                image_url = f"{domain}{image_url}"
            return image_url
        else:
            logger.error(f"Image file not found: {image_path}")
            return None


def store_poster_image(image_bytes: bytes, filename: str = None) -> tuple[str, str, Optional[str]]:
    """
    Store poster image using the configured storage mode.
    This is the main entry point for storing poster images.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate if not provided)
    
    Returns:
        Tuple of (saved_path, image_url, public_url)
        - saved_path: Django storage path
        - image_url: Local media URL
        - public_url: Public URL for sharing (Cloudinary URL or local media URL)
    """
    storage_mode = get_storage_mode()
    
    # Always save locally first (for backup and local access)
    saved_path, image_url = save_poster_image(image_bytes, filename)
    logger.info(f"Image saved locally to: {saved_path}")
    
    # Get public URL based on storage mode
    public_url = None
    if storage_mode == 'cloudinary':
        # Upload to Cloudinary for public sharing
        logger.info("Uploading to Cloudinary...")
        public_url = upload_to_cloudinary(saved_path)
        if public_url:
            logger.info(f"Successfully uploaded to Cloudinary: {public_url}")
        else:
            logger.warning("Cloudinary upload failed, falling back to local URL")
            public_url = image_url
    else:
        # Use local URL as public URL
        public_url = image_url
        logger.info(f"Using local storage URL: {public_url}")
    
    return saved_path, image_url, public_url


def create_and_store_shareable_page(image_url: str, caption: str, full_caption: str) -> Optional[str]:
    """
    Create and store a shareable HTML page with Open Graph tags.
    Uses Cloudinary in cloudinary mode, local storage in local mode.
    
    Args:
        image_url: URL of the poster image
        caption: Short caption for the poster
        full_caption: Full caption/description
    
    Returns:
        URL of the shareable HTML page, or None if creation fails
    """
    storage_mode = get_storage_mode()
    
    # Create HTML content
    html_content = create_shareable_html_page(image_url, caption, full_caption)
    
    if storage_mode == 'cloudinary':
        # Upload HTML to Cloudinary
        logger.info("Uploading HTML page to Cloudinary...")
        filename = f"poster_{int(time.time())}"
        html_url = upload_html_to_cloudinary(html_content, filename=filename)
        if html_url:
            logger.info(f"Successfully uploaded HTML page to Cloudinary: {html_url}")
        return html_url
    else:
        # Save HTML to local storage
        logger.info("Saving HTML page to local storage...")
        filename = f"poster_{uuid.uuid4().hex[:8]}_{int(time.time())}.html"
        output_path = f"generated/{filename}"
        
        try:
            saved_path = default_storage.save(output_path, ContentFile(html_content.encode('utf-8')))
            html_url = default_storage.url(saved_path)
            
            # Ensure full URL
            if not html_url.startswith('http'):
                domain = get_domain_url()
                html_url = f"{domain}{html_url}"
            
            logger.info(f"Successfully saved HTML page locally: {html_url}")
            return html_url
        except Exception as e:
            logger.error(f"Failed to save HTML page locally: {str(e)}")
            return None

