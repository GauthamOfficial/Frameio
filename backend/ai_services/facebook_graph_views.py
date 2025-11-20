"""
Facebook Graph API views for server-side posting (future use)
Requires Facebook Page access token stored securely on server
"""
import os
import logging
import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.cache import cache
from .models import GeneratedPoster

logger = logging.getLogger(__name__)

# Facebook Graph API base URL
FACEBOOK_GRAPH_API_URL = 'https://graph.facebook.com/v18.0'


def get_facebook_page_token(page_id: str = None):
    """
    Get Facebook Page access token from secure storage.
    In production, this should be stored encrypted in database or secure vault.
    
    Args:
        page_id: Optional Facebook Page ID
        
    Returns:
        Page access token or None
    """
    # For now, get from environment variable
    # In production, store in database with encryption
    token = os.getenv('FB_PAGE_ACCESS_TOKEN')
    
    if not token:
        logger.warning("Facebook Page access token not configured")
        return None
    
    # TODO: In production, implement:
    # 1. Store tokens in database (encrypted)
    # 2. Associate with organization/user
    # 3. Handle token refresh
    # 4. Support multiple pages
    
    return token


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_to_facebook_page(request):
    """
    POST /api/social/facebook/post/
    
    Post a poster to a Facebook Page using Graph API.
    Requires admin authentication and valid Page access token.
    
    Body:
    {
        "poster_id": "uuid",
        "page_id": "facebook_page_id",  // Optional, uses default if not provided
        "message": "Custom message",     // Optional, uses poster caption if not provided
    }
    
    Returns:
    {
        "success": true,
        "post_id": "facebook_post_id",
        "url": "https://facebook.com/...",
        "message": "Post published successfully"
    }
    """
    try:
        data = request.data
        poster_id = data.get('poster_id')
        page_id = data.get('page_id')
        custom_message = data.get('message')
        
        if not poster_id:
            return Response({
                "success": False,
                "error": "poster_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get poster
        try:
            poster = GeneratedPoster.objects.get(id=poster_id)
        except GeneratedPoster.DoesNotExist:
            return Response({
                "success": False,
                "error": "Poster not found"
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions (user must own poster or be admin)
        user = request.user
        if poster.user != user and not user.is_staff:
            # Check organization access
            if hasattr(user, 'organization') and poster.organization != user.organization:
                return Response({
                    "success": False,
                    "error": "Permission denied"
                }, status=status.HTTP_403_FORBIDDEN)
        
        # Get Facebook Page access token
        page_token = get_facebook_page_token(page_id)
        if not page_token:
            return Response({
                "success": False,
                "error": "Facebook Page access token not configured. Please contact administrator."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Build message (use custom message or poster caption)
        message = custom_message or poster.full_caption or poster.caption
        if poster.hashtags:
            hashtags_str = ' '.join(poster.hashtags)
            message = f"{message}\n\n{hashtags_str}"
        
        # Ensure image URL is absolute and public
        image_url = poster.image_url
        if not image_url.startswith(('http://', 'https://')):
            from .utils.storage import get_public_image_url
            image_url = get_public_image_url(image_url, request)
        
        # Use Facebook Graph API to post photo with URL
        # Option 1: Post photo with URL (recommended for external images)
        graph_url = f"{FACEBOOK_GRAPH_API_URL}/{page_id}/photos"
        
        params = {
            'access_token': page_token,
            'url': image_url,
            'caption': message,
            'published': 'true'
        }
        
        # Make request to Facebook Graph API
        try:
            response = requests.post(graph_url, params=params, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            
            if 'id' in result:
                # Post successful
                post_id = result['id']
                
                # Get post URL (construct from page_id and post_id)
                post_url = f"https://www.facebook.com/{post_id}"
                
                logger.info(f"Successfully posted to Facebook Page {page_id}: {post_id}")
                
                return Response({
                    "success": True,
                    "post_id": post_id,
                    "url": post_url,
                    "message": "Post published successfully to Facebook Page"
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Facebook API response missing 'id': {result}")
                return Response({
                    "success": False,
                    "error": "Facebook API returned unexpected response",
                    "details": result
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except requests.exceptions.HTTPError as e:
            error_data = e.response.json() if e.response else {}
            error_message = error_data.get('error', {}).get('message', str(e))
            error_code = error_data.get('error', {}).get('code', 'UNKNOWN')
            
            logger.error(f"Facebook API error: {error_code} - {error_message}")
            
            return Response({
                "success": False,
                "error": f"Facebook API error: {error_message}",
                "error_code": error_code
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Facebook API: {str(e)}")
            return Response({
                "success": False,
                "error": "Failed to connect to Facebook API"
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        logger.error(f"Error posting to Facebook: {str(e)}")
        return Response({
            "success": False,
            "error": str(e) if settings.DEBUG else "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_facebook_pages(request):
    """
    GET /api/social/facebook/pages/
    
    Get list of Facebook Pages associated with the user's access token.
    Requires user access token (not implemented - placeholder for future).
    
    Returns:
    {
        "success": true,
        "pages": [
            {
                "id": "page_id",
                "name": "Page Name",
                "access_token": "token"  // Only if user has admin rights
            }
        ]
    }
    """
    # TODO: Implement OAuth flow to get user access token
    # Then exchange for Page access tokens
    
    return Response({
        "success": False,
        "error": "Not implemented. Requires Facebook OAuth integration.",
        "message": "This endpoint requires Facebook OAuth to be configured. Please contact administrator."
    }, status=status.HTTP_501_NOT_IMPLEMENTED)




