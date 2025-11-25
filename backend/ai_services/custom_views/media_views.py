"""
Views for serving media files with proper CORS headers for Facebook sharing.
"""
import os
import logging
from django.conf import settings
from django.http import Http404
from django.views.decorators.cache import cache_control
from django.views.static import serve as static_serve

logger = logging.getLogger(__name__)


@cache_control(public=True, max_age=3600)
def serve_media_file(request, path):
    """
    Serve media files with proper CORS headers for Facebook sharing.
    
    This view ensures that media files are publicly accessible and include
    CORS headers so they can be accessed by Facebook's crawler.
    """
    # Build full file path
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    
    # Check if file exists
    if not os.path.exists(file_path):
        raise Http404("File not found")
    
    # Use Django's static file serving with CORS headers
    response = static_serve(request, path, document_root=settings.MEDIA_ROOT)
    
    # Add CORS headers for Facebook sharing
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'GET, HEAD, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    response['Access-Control-Max-Age'] = '3600'
    
    # Set proper content type for images
    if path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
        if path.lower().endswith('.png'):
            response['Content-Type'] = 'image/png'
        elif path.lower().endswith(('.jpg', '.jpeg')):
            response['Content-Type'] = 'image/jpeg'
        elif path.lower().endswith('.gif'):
            response['Content-Type'] = 'image/gif'
        elif path.lower().endswith('.webp'):
            response['Content-Type'] = 'image/webp'
    
    # Cache control headers for better performance
    response['Cache-Control'] = 'public, max-age=3600'
    
    return response

