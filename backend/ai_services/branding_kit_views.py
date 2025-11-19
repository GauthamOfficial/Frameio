"""
Branding Kit API Views
Django REST Framework views for branding kit generation endpoints
"""
import os
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .branding_kit_service import BrandingKitService
from .models import GeneratedBrandingKit

logger = logging.getLogger(__name__)

# Initialize the branding kit service
branding_kit_service = BrandingKitService()


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_branding_kit(request):
    """
    POST /api/ai/branding-kit/generate/
    Generate complete branding kit from text prompt
    
    Body: {
        "prompt": "describe your logo idea",
        "style": "modern"  // Optional: modern, vintage, minimalist, etc.
    }
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        style = data.get('style', 'modern')
        
        if not prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not branding_kit_service.is_available():
            return Response({
                'success': False,
                'error': 'Branding kit service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Generate the branding kit
        result = branding_kit_service.generate_branding_kit(prompt, style)
        
        if result.get('success'):
            # Get user and organization from request if available
            user = None
            organization = None
            
            # Check if user is authenticated
            logger.info(f"Request user: {request.user}, is_authenticated: {getattr(request.user, 'is_authenticated', False)}")
            
            if hasattr(request, 'user') and request.user and getattr(request.user, 'is_authenticated', False):
                user = request.user
                logger.info(f"Authenticated user: {user.email if hasattr(user, 'email') else user.username}")
                
                # Try to get organization from user
                if hasattr(user, 'organization') and user.organization:
                    organization = user.organization
                    logger.info(f"Found organization from user: {organization}")
                else:
                    try:
                        from users.models import CompanyProfile
                        company_profile = getattr(user, 'company_profile', None)
                        if company_profile and hasattr(company_profile, 'organization') and company_profile.organization:
                            organization = company_profile.organization
                            logger.info(f"Found organization from company profile: {organization}")
                    except Exception as e:
                        logger.warning(f"Could not get organization: {e}")
            else:
                logger.warning("No authenticated user found - branding kit will be saved without user association")
            
            # Save the generated branding kit to database
            try:
                branding_kit_data = result.get('branding_kit', {})
                logo_data = branding_kit_data.get('logo', {})
                palette_data = branding_kit_data.get('color_palette', {})
                
                # Check if logo and palette data exist
                logo_data_str = logo_data.get('data', '') if logo_data else ''
                palette_data_str = palette_data.get('data', '') if palette_data else ''
                
                logger.info(f"Saving branding kit - Logo data length: {len(logo_data_str)}, Palette data length: {len(palette_data_str)}")
                
                branding_kit = GeneratedBrandingKit.objects.create(
                    organization=organization,
                    user=user,
                    prompt=prompt,
                    style=style,
                    logo_data=logo_data_str,
                    logo_format=logo_data.get('format', 'png') if logo_data else 'png',
                    color_palette_data=palette_data_str,
                    color_palette_format=palette_data.get('format', 'png') if palette_data else 'png',
                    colors=result.get('used_colors', [])
                )
                logger.info(f"Branding kit saved to database with ID: {branding_kit.id}, User: {user.email if user and hasattr(user, 'email') else 'None'}")
            except Exception as e:
                logger.error(f"Failed to save branding kit to database: {str(e)}", exc_info=True)
                # Continue even if save fails
            
            return Response({
                'success': True,
                'message': 'Branding kit generated successfully',
                'data': result
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_branding_kit: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_logo(request):
    """
    POST /api/ai/branding-kit/logo/
    Generate logo from text prompt
    
    Body: {
        "prompt": "describe your logo idea",
        "style": "modern"  // Optional
    }
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        style = data.get('style', 'modern')
        
        if not prompt:
            return Response({
                'success': False,
                'error': 'Prompt is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not branding_kit_service.is_available():
            return Response({
                'success': False,
                'error': 'Branding kit service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Generate the logo
        result = branding_kit_service.generate_logo(prompt, style)
        
        if result.get('success'):
            return Response({
                'success': True,
                'message': 'Logo generated successfully',
                'data': result
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_logo: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_color_palette(request):
    """
    POST /api/ai/branding-kit/colors/
    Generate color palette from a logo image (preferred) or from text prompt
    
    Body: {
        // Preferred input:
        "logo": "<base64 image>",
        "num_colors": 5,
        
        // Backward-compatible fallback:
        "prompt": "describe your brand"
    }
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        logo_b64 = data.get('logo') or data.get('logo_base64')
        num_colors = data.get('num_colors', 5)
        
        if not branding_kit_service.is_available():
            return Response({
                'success': False,
                'error': 'Branding kit service not available'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Prefer extracting from provided logo if present
        if logo_b64:
            result = branding_kit_service.generate_color_palette_from_logo(logo_b64, num_colors)
        else:
            if not prompt:
                return Response({
                    'success': False,
                    'error': 'Provide either logo (base64) or prompt'
                }, status=status.HTTP_400_BAD_REQUEST)
            # Fallback to prompt-based color palette
            result = branding_kit_service.generate_color_palette(prompt, num_colors)
        
        if result.get('success'):
            return Response({
                'success': True,
                'message': 'Color palette generated successfully',
                'data': result
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'error': result.get('error', 'Unknown error')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_color_palette: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def branding_kit_status(request):
    """
    GET /api/ai/branding-kit/status/
    Check branding kit service status
    """
    try:
        is_available = branding_kit_service.is_available()
        
        return Response({
            'success': True,
            'service_available': is_available,
            'message': 'Branding kit service is available' if is_available else 'Branding kit service is not available'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in branding_kit_status: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def list_branding_kits(request):
    """
    GET /api/ai/branding-kit/history/
    List all generated branding kits for the current user/organization
    
    Query params:
    - limit: Number of branding kits to return (default: 50)
    - offset: Offset for pagination (default: 0)
    """
    try:
        # Get user from request if authenticated
        user = None
        organization = None
        
        logger.info(f"List branding kits - Request user: {request.user}, is_authenticated: {getattr(request.user, 'is_authenticated', False)}")
        
        if hasattr(request, 'user') and request.user and getattr(request.user, 'is_authenticated', False):
            user = request.user
            logger.info(f"List branding kits - Authenticated user: {user.email if hasattr(user, 'email') else user.username}")
            
            # Try to get organization from user
            if hasattr(user, 'organization') and user.organization:
                organization = user.organization
                logger.info(f"List branding kits - Found organization from user: {organization}")
            else:
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and hasattr(company_profile, 'organization') and company_profile.organization:
                        organization = company_profile.organization
                        logger.info(f"List branding kits - Found organization from company profile: {organization}")
                except Exception as e:
                    logger.warning(f"Could not get organization: {e}")
        
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        logger.info(f"List branding kits - Query params: limit={limit}, offset={offset}")
        
        # Build queryset
        queryset = GeneratedBrandingKit.objects.all()
        logger.info(f"List branding kits - Total branding kits in DB: {queryset.count()}")
        
        # Filter by organization if available
        if organization:
            queryset = queryset.filter(organization=organization)
            logger.info(f"List branding kits - Filtered by organization: {queryset.count()} kits")
        elif user:
            queryset = queryset.filter(user=user)
            logger.info(f"List branding kits - Filtered by user: {queryset.count()} kits")
        else:
            # In development, if no user is authenticated, show all kits
            # In production, this should return empty
            from django.conf import settings
            if settings.DEBUG:
                logger.warning("List branding kits - No authenticated user, showing all kits (DEBUG mode)")
            else:
                queryset = queryset.none()
                logger.warning("List branding kits - No authenticated user, returning empty (PRODUCTION mode)")
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        total_count = queryset.count()
        branding_kits = queryset[offset:offset + limit]
        logger.info(f"List branding kits - Returning {len(branding_kits)} kits (total: {total_count})")
        
        # Serialize branding kits
        branding_kits_data = []
        for kit in branding_kits:
            branding_kits_data.append({
                'id': str(kit.id),
                'prompt': kit.prompt,
                'style': kit.style,
                'logo': {
                    'data': kit.logo_data,
                    'format': kit.logo_format,
                    'url': kit.logo_url
                } if kit.logo_data else None,
                'color_palette': {
                    'data': kit.color_palette_data,
                    'format': kit.color_palette_format,
                    'url': kit.color_palette_url
                } if kit.color_palette_data else None,
                'colors': kit.colors,
                'created_at': kit.created_at.isoformat(),
                'updated_at': kit.updated_at.isoformat()
            })
        
        return Response({
            'success': True,
            'results': branding_kits_data,
            'count': total_count,
            'limit': limit,
            'offset': offset
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing branding kits: {str(e)}")
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_branding_kit(request, kit_id):
    """
    DELETE /api/ai/branding-kit/{kit_id}/delete/
    Delete a specific branding kit by ID
    """
    try:
        kit = GeneratedBrandingKit.objects.get(id=kit_id)
        
        # Check permissions (user or organization match)
        user = None
        organization = None
        
        if request.user and request.user.is_authenticated:
            user = request.user
            if hasattr(user, 'organization'):
                organization = user.organization
            else:
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and hasattr(company_profile, 'organization'):
                        organization = company_profile.organization
                except Exception:
                    pass
        
        # Check if user has access
        if organization and kit.organization != organization:
            return Response({
                'success': False,
                'error': 'Branding kit not found or access denied'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user and kit.user and kit.user != user:
            if not organization or kit.organization != organization:
                return Response({
                    'success': False,
                    'error': 'Branding kit not found or access denied'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete the branding kit record
        kit.delete()
        logger.info(f"Deleted branding kit with ID: {kit_id}")
        
        return Response({
            'success': True,
            'message': 'Branding kit deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except GeneratedBrandingKit.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Branding kit not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting branding kit: {str(e)}")
        return Response({
            'success': False,
            'error': str(e) if settings.DEBUG else 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def test_color_detection(request):
    """
    POST /api/ai/branding-kit/test-colors/
    Test color detection in prompts
    """
    try:
        data = request.data
        prompt = data.get('prompt', '')
        
        # Enhanced color detection (same as in service)
        color_keywords = [
            'blue', 'red', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white', 
            'gray', 'grey', 'gold', 'silver', 'navy', 'teal', 'coral', 'maroon', 'beige', 'cream',
            'cyan', 'magenta', 'lime', 'indigo', 'violet', 'turquoise', 'amber', 'crimson', 'emerald',
            'sapphire', 'ruby', 'pearl', 'bronze', 'copper', 'platinum', 'charcoal', 'ivory', 'tan',
            'burgundy', 'forest green', 'sky blue', 'royal blue', 'deep blue', 'light blue', 'dark blue',
            'bright red', 'deep red', 'light green', 'dark green', 'bright yellow', 'dark yellow',
            'hot pink', 'deep pink', 'light pink', 'dark purple', 'light purple', 'bright orange',
            'dark orange', 'light brown', 'dark brown', 'light gray', 'dark gray', 'steel blue',
            'olive green', 'mint green', 'lavender', 'rose gold', 'champagne', 'coffee', 'chocolate'
        ]
        
        import re
        prompt_lower = prompt.lower()
        mentioned_colors = [color for color in color_keywords if color.lower() in prompt_lower]
        hex_colors = re.findall(r'#[0-9a-fA-F]{6}', prompt)
        rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', prompt)
        
        return Response({
            'success': True,
            'prompt': prompt,
            'detected_colors': {
                'mentioned_colors': mentioned_colors,
                'hex_colors': hex_colors,
                'rgb_colors': rgb_colors,
                'total_detected': len(mentioned_colors) + len(hex_colors) + len(rgb_colors)
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in test_color_detection: {str(e)}")
        return Response({
            'success': False,
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
