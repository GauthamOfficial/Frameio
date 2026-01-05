"""
Storage handler for poster images.
Migrated to use Amazon S3 for file storage instead of local EC2 disk.
"""
import os
import logging
import time
import uuid
from typing import Optional
from django.conf import settings
from utils.s3_storage import upload_file_to_s3, generate_s3_key, file_exists_in_s3

logger = logging.getLogger(__name__)

# Import HTML page creation utility
from .cloudinary_utils import create_shareable_html_page


def get_domain_url() -> str:
    """
    Get the domain URL (kept for backward compatibility).
    Note: With S3, URLs are generated directly from S3, so this is mainly for legacy code.
    
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
    Save poster image to S3 storage.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate if not provided)
    
    Returns:
        Tuple of (s3_key, image_url)
        - s3_key: S3 object key (path within bucket)
        - image_url: Public S3 URL
    """
    if not filename:
        filename = f"poster_{uuid.uuid4().hex[:8]}_{int(time.time())}.png"
    
    # Generate S3 key (path) for the file
    # Store in 'generated' folder with date prefix
    s3_key = generate_s3_key('generated', filename, date_prefix=True)
    
    # Upload to S3 (not local disk)
    image_url = upload_file_to_s3(
        file_content=image_bytes,
        s3_key=s3_key,
        content_type='image/png'
    )
    
    logger.info(f"Poster image uploaded to S3: {s3_key} -> {image_url}")
    
    return s3_key, image_url


def upload_poster_image(image_path: str) -> Optional[str]:
    """
    Get public URL for poster image from S3.
    
    Args:
        image_path: S3 key (path) to the image file (e.g., 'generated/2024/01/15/poster.png')
    
    Returns:
        Public S3 URL of the image, or None if file not found
    """
    logger.info(f"Getting public URL for S3: {image_path}")
    
    # Check if file exists in S3
    if file_exists_in_s3(image_path):
        # Generate S3 public URL
        bucket_name = os.getenv('AWS_S3_BUCKET')
        region = os.getenv('AWS_REGION')
        
        if not bucket_name or not region:
            logger.error("AWS_S3_BUCKET or AWS_REGION not set")
            return None
        
        image_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{image_path}"
        return image_url
    else:
        logger.error(f"Image file not found in S3: {image_path}")
        return None


def store_poster_image(image_bytes: bytes, filename: str = None) -> tuple[str, str, Optional[str]]:
    """
    Store poster image using S3 storage.
    This is the main entry point for storing poster images.
    
    Args:
        image_bytes: Image data as bytes
        filename: Optional filename (will generate if not provided)
    
    Returns:
        Tuple of (s3_key, image_url, public_url)
        - s3_key: S3 object key (path within bucket)
        - image_url: Public S3 URL
        - public_url: Public URL for sharing (same as image_url for S3)
    """
    # Upload to S3 (not local disk)
    s3_key, image_url = save_poster_image(image_bytes, filename)
    logger.info(f"Image uploaded to S3: {s3_key}")
    
    # Use S3 URL as public URL
    public_url = image_url
    logger.info(f"Using S3 URL: {public_url}")
    
    return s3_key, image_url, public_url


def create_and_store_shareable_page(image_url: str, caption: str, full_caption: str) -> Optional[str]:
    """
    Create and store a shareable HTML page with Open Graph tags.
    Uses S3 storage.
    
    Args:
        image_url: URL of the poster image
        caption: Short caption for the poster
        full_caption: Full caption/description
    
    Returns:
        URL of the shareable HTML page, or None if creation fails
    """
    # Create HTML content
    html_content = create_shareable_html_page(image_url, caption, full_caption)
    
    # Upload HTML to S3 (not local disk)
    logger.info("Uploading HTML page to S3...")
    filename = f"poster_{uuid.uuid4().hex[:8]}_{int(time.time())}.html"
    
    # Generate S3 key (path) for the HTML file
    s3_key = generate_s3_key('generated', filename, date_prefix=True)
    
    try:
        html_url = upload_file_to_s3(
            file_content=html_content.encode('utf-8'),
            s3_key=s3_key,
            content_type='text/html'
        )
        
        logger.info(f"Successfully uploaded HTML page to S3: {html_url}")
        return html_url
    except Exception as e:
        logger.error(f"Failed to upload HTML page to S3: {str(e)}")
        return None
