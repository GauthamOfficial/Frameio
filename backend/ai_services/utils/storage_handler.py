"""
Storage handler for poster images.
Uses local server storage with public URLs based on DOMAIN_URL.
"""
import os
import logging
import time
import uuid
from typing import Optional
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

# Import HTML page creation utility
from .cloudinary_utils import create_shareable_html_page


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
    Get public URL for poster image from local storage.
    
    Args:
        image_path: Path to the image file (Django storage path)
    
    Returns:
        Public URL of the image, or None if file not found
    """
    logger.info(f"Getting public URL for local storage: {image_path}")
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
    Store poster image using local storage.
    This is the main entry point for storing poster images.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate if not provided)
    
    Returns:
        Tuple of (saved_path, image_url, public_url)
        - saved_path: Django storage path
        - image_url: Local media URL
        - public_url: Public URL for sharing (same as image_url for local storage)
    """
    # Save locally
    saved_path, image_url = save_poster_image(image_bytes, filename)
    logger.info(f"Image saved locally to: {saved_path}")
    
    # Use local URL as public URL
    public_url = image_url
    logger.info(f"Using local storage URL: {public_url}")
    
    return saved_path, image_url, public_url


def create_and_store_shareable_page(image_url: str, caption: str, full_caption: str) -> Optional[str]:
    """
    Create and store a shareable HTML page with Open Graph tags.
    Uses local storage.
    
    Args:
        image_url: URL of the poster image
        caption: Short caption for the poster
        full_caption: Full caption/description
    
    Returns:
        URL of the shareable HTML page, or None if creation fails
    """
    # Create HTML content
    html_content = create_shareable_html_page(image_url, caption, full_caption)
    
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
