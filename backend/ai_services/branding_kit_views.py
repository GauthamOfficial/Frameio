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
    Generate color palette from text prompt
    
    Body: {
        "prompt": "describe your brand",
        "num_colors": 5  // Optional, default 5
    }
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        num_colors = data.get('num_colors', 5)
        
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
        
        # Generate the color palette
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
