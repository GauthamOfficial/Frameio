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
from .branding_kit_service import BrandingKitService

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
