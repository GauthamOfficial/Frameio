"""
Storage utilities for handling public and signed image URLs
Supports both local storage and AWS S3
"""
import os
import logging
from typing import Optional, Tuple
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def get_public_image_url(image_url: str, request=None) -> str:
    """
    Get a public absolute URL for an image.
    
    Args:
        image_url: The image URL (can be relative or absolute)
        request: Django request object for building absolute URLs
        
    Returns:
        Absolute public URL for the image
    """
    # If already an absolute URL (http/https), return as-is
    if image_url.startswith(('http://', 'https://')):
        return image_url
    
    # If we have a request, use it to build absolute URL
    if request:
        return request.build_absolute_uri(image_url)
    
    # Fallback: construct from settings
    # Try to get from environment or settings
    api_base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
    if not api_base_url.endswith('/'):
        api_base_url += '/'
    
    # Remove leading slash from image_url if present
    if image_url.startswith('/'):
        image_url = image_url[1:]
    
    return f"{api_base_url}{image_url}"


def get_signed_image_url(image_url: str, expiration: int = 600, request=None) -> Optional[str]:
    """
    Get a signed (presigned) URL for a private image (e.g., S3).
    For local storage, returns public URL.
    
    Args:
        image_url: The image URL or S3 key
        expiration: URL expiration time in seconds (default: 600 = 10 minutes)
        request: Django request object
        
    Returns:
        Signed URL if S3 is configured, otherwise public URL
    """
    # Check if S3 is configured
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    if aws_access_key and aws_secret_key and aws_bucket:
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            # Parse S3 key from URL
            # If image_url is already an S3 URL, extract the key
            if 's3.amazonaws.com' in image_url or 's3.' in image_url:
                parsed = urlparse(image_url)
                s3_key = parsed.path.lstrip('/')
            else:
                # Assume it's already a key
                s3_key = image_url.lstrip('/')
            
            # Create S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
            )
            
            # Generate presigned URL
            presigned_url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': aws_bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            
            logger.info(f"Generated presigned URL for S3 key: {s3_key}")
            return presigned_url
            
        except ImportError:
            logger.warning("boto3 not installed, falling back to public URL")
        except ClientError as e:
            logger.error(f"Error generating presigned URL: {e}")
        except Exception as e:
            logger.error(f"Unexpected error generating presigned URL: {e}")
    
    # Fallback to public URL
    return get_public_image_url(image_url, request)


def validate_image_for_sharing(image_url: str, width: Optional[int] = None, height: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate that an image meets Facebook sharing requirements.
    
    Facebook requirements:
    - Minimum size: 200x200 pixels
    - Recommended: 1200x630 pixels (1.91:1 aspect ratio)
    - Max file size: 8MB
    - Supported formats: JPEG, PNG, GIF, WebP
    
    Args:
        image_url: The image URL
        width: Image width in pixels
        height: Image height in pixels
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check dimensions if provided
    if width and height:
        if width < 200 or height < 200:
            return False, f"Image dimensions ({width}x{height}) are below Facebook's minimum requirement of 200x200 pixels"
        
        # Check aspect ratio (warn but don't fail)
        aspect_ratio = width / height
        if aspect_ratio < 0.8 or aspect_ratio > 2.0:
            logger.warning(f"Image aspect ratio ({aspect_ratio:.2f}) may not display optimally on Facebook (recommended: 1.91:1)")
    
    # Check file format (basic check from URL)
    image_url_lower = image_url.lower()
    supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(image_url_lower.endswith(ext) for ext in supported_formats):
        # Don't fail, just warn - URL might not have extension
        logger.warning(f"Image URL doesn't have a recognized extension: {image_url}")
    
    return True, None


def ensure_public_access(image_path: str) -> bool:
    """
    Ensure an image file is publicly accessible.
    For S3, this would set the ACL to public-read.
    For local storage, files are typically already public if served correctly.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        True if successful, False otherwise
    """
    # Check if S3 is configured
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    aws_bucket = os.getenv('AWS_STORAGE_BUCKET_NAME')
    
    if aws_access_key and aws_secret_key and aws_bucket:
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
            )
            
            # Extract S3 key from path
            if 's3.amazonaws.com' in image_path or 's3.' in image_path:
                parsed = urlparse(image_path)
                s3_key = parsed.path.lstrip('/')
            else:
                s3_key = image_path.lstrip('/')
            
            # Set ACL to public-read
            s3_client.put_object_acl(
                Bucket=aws_bucket,
                Key=s3_key,
                ACL='public-read'
            )
            
            logger.info(f"Set public-read ACL for S3 key: {s3_key}")
            return True
            
        except ImportError:
            logger.warning("boto3 not installed, cannot set S3 ACL")
        except ClientError as e:
            logger.error(f"Error setting S3 ACL: {e}")
        except Exception as e:
            logger.error(f"Unexpected error setting S3 ACL: {e}")
            return False
    
    # For local storage, assume it's already public if MEDIA_URL is configured
    return True



