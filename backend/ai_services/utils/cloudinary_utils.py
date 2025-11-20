"""
Cloudinary utility functions for uploading images
"""
import os
import logging
import time
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)

try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    CLOUDINARY_AVAILABLE = True
except ImportError:
    logger.warning("Cloudinary not available. Please install: pip install cloudinary")
    CLOUDINARY_AVAILABLE = False


def create_shareable_html_page(image_url: str, caption: str, full_caption: str) -> str:
    """
    Create a simple HTML page with Open Graph meta tags for Facebook sharing.
    Returns the HTML content as a string.
    """
    # Escape HTML special characters for meta tags
    def escape_html(text: str) -> str:
        if not text:
            return ""
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    safe_caption = escape_html(caption[:60] if caption else "AI Generated Poster")
    # Use longer description - Facebook allows up to 300 characters
    safe_full_caption = escape_html(full_caption[:300] if full_caption else caption[:300] if caption else "Check out this amazing AI-generated poster!")
    safe_image_url = image_url.replace('&', '&amp;')
    
    # Note: og:url will be set after HTML is uploaded (we don't know the HTML URL yet)
    # We'll update it in a second pass, or use a placeholder that gets replaced
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_caption}</title>
    
    <!-- Open Graph Meta Tags for Facebook -->
    <meta property="og:title" content="{safe_caption}" />
    <meta property="og:description" content="{safe_full_caption}" />
    <meta property="og:image" content="{safe_image_url}" />
    <meta property="og:image:secure_url" content="{safe_image_url}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:image:type" content="image/png" />
    <meta property="og:type" content="article" />
    <!-- og:url will be set after upload -->
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{safe_caption}" />
    <meta name="twitter:description" content="{safe_full_caption}" />
    <meta name="twitter:image" content="{safe_image_url}" />
    
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        h1 {{
            color: #333;
            margin-top: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{safe_image_url}" alt="{safe_caption}" />
        <h1>{safe_caption}</h1>
        <p>{safe_full_caption}</p>
    </div>
</body>
</html>"""
    return html_content


def upload_html_to_cloudinary(html_content: str, filename: str = None) -> Optional[str]:
    """
    Upload HTML content to Cloudinary and return the public URL.
    
    Args:
        html_content: HTML content as string
        filename: Optional filename for the HTML file
    
    Returns:
        Public URL of the uploaded HTML file, or None if upload fails
    """
    if not CLOUDINARY_AVAILABLE:
        logger.error("Cloudinary is not available. Please install cloudinary package.")
        return None
    
    # Get Cloudinary credentials from environment
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        logger.error("Cloudinary credentials not configured.")
        return None
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    
    try:
        from io import BytesIO
        
        # Convert HTML string to bytes
        html_bytes = html_content.encode('utf-8')
        html_file = BytesIO(html_bytes)
        
        # Upload to Cloudinary as raw file
        result = cloudinary.uploader.upload(
            html_file,
            folder="posters",
            resource_type="raw",
            format="html",
            public_id=filename or f"share_{int(time.time())}"
        )
        
        public_url = result.get('secure_url') or result.get('url')
        logger.info(f"Successfully uploaded HTML page to Cloudinary: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Failed to upload HTML to Cloudinary: {str(e)}")
        return None


def create_shareable_html_page(image_url: str, caption: str, full_caption: str) -> str:
    """
    Create a simple HTML page with Open Graph meta tags for Facebook sharing.
    Returns the HTML content as a string.
    """
    # Escape HTML special characters
    def escape_html(text: str) -> str:
        return (text.replace('&', '&amp;')
                   .replace('<', '&lt;')
                   .replace('>', '&gt;')
                   .replace('"', '&quot;')
                   .replace("'", '&#39;'))
    
    safe_caption = escape_html(caption[:60])
    safe_full_caption = escape_html(full_caption[:200])
    safe_image_url = image_url.replace('&', '&amp;')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_caption}</title>
    
    <!-- Open Graph Meta Tags for Facebook -->
    <meta property="og:title" content="{safe_caption}" />
    <meta property="og:description" content="{safe_full_caption}" />
    <meta property="og:image" content="{safe_image_url}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="1200" />
    <meta property="og:type" content="article" />
    <meta property="og:url" content="{safe_image_url}" />
    
    <!-- Twitter Card Meta Tags -->
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{safe_caption}" />
    <meta name="twitter:description" content="{safe_full_caption}" />
    <meta name="twitter:image" content="{safe_image_url}" />
    
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background: #f0f0f0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }}
        .container {{
            max-width: 800px;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        h1 {{
            color: #333;
            margin-top: 20px;
        }}
        p {{
            color: #666;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="container">
        <img src="{safe_image_url}" alt="{safe_caption}" />
        <h1>{safe_caption}</h1>
        <p>{safe_full_caption}</p>
    </div>
</body>
</html>"""
    return html_content


def upload_to_cloudinary(image_path: str) -> Optional[str]:
    """
    Upload an image file to Cloudinary and return the public URL.
    
    Args:
        image_path: Path to the image file (can be local file path or Django storage path)
    
    Returns:
        Public URL of the uploaded image, or None if upload fails
    """
    if not CLOUDINARY_AVAILABLE:
        logger.error("Cloudinary is not available. Please install cloudinary package.")
        return None
    
    # Get Cloudinary credentials from environment
    cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')
    api_secret = os.getenv('CLOUDINARY_API_SECRET')
    
    if not all([cloud_name, api_key, api_secret]):
        logger.error("Cloudinary credentials not configured. Please set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET environment variables.")
        return None
    
    # Configure Cloudinary
    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret
    )
    
    try:
        # Check if image_path is a Django storage path or absolute file path
        from django.core.files.storage import default_storage
        
        # Try to get the actual file path
        if default_storage.exists(image_path):
            # If it's a storage path, get the actual file
            with default_storage.open(image_path, 'rb') as f:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(
                    f,
                    folder="posters",
                    resource_type="image",
                    format="png"
                )
                public_url = result.get('secure_url') or result.get('url')
                logger.info(f"Successfully uploaded image to Cloudinary: {public_url}")
                return public_url
        elif os.path.exists(image_path):
            # If it's an absolute file path
            with open(image_path, 'rb') as f:
                result = cloudinary.uploader.upload(
                    f,
                    folder="posters",
                    resource_type="image",
                    format="png"
                )
                public_url = result.get('secure_url') or result.get('url')
                logger.info(f"Successfully uploaded image to Cloudinary: {public_url}")
                return public_url
        else:
            logger.error(f"Image file not found: {image_path}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to upload image to Cloudinary: {str(e)}")
        return None

