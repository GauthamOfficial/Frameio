"""
AI Poster Generation API Views
Django REST Framework views for poster generation endpoints
"""
import os
import time
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from .ai_poster_service import AIPosterService

logger = logging.getLogger(__name__)

# Initialize the AI poster service
ai_poster_service = AIPosterService()


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_poster(request):
    """
    POST /api/ai-poster/generate_poster/
    Generate poster image from text prompt only
    
    Body: {
        "prompt": "Create a modern textile poster for a silk saree brand",
        "aspect_ratio": "4:5"  // Optional: 1:1, 16:9, 4:5
    }
    """
    try:
        data = request.data
        prompt = data.get('prompt')
        aspect_ratio = data.get('aspect_ratio', '1:1')
        
        if not prompt:
            return Response({
                "success": False,
                "error": "Prompt is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate aspect ratio
        valid_ratios = ['1:1', '16:9', '4:5']
        if aspect_ratio not in valid_ratios:
            aspect_ratio = '1:1'
        
        logger.info(f"Generating poster with prompt: {prompt[:50]}...")
        
        # Check if service is available first
        if not ai_poster_service.is_available():
            return Response({
                "success": False,
                "error": "AI poster service is not available. Please check configuration."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Generate poster using AI service
        result = ai_poster_service.generate_from_prompt(prompt, aspect_ratio)
        
        if result.get('status') == 'success':
            return Response({
                "success": True,
                "message": "Poster generated successfully",
                "image_path": result.get('image_path'),
                "image_url": result.get('image_url'),
                "filename": result.get('filename'),
                "aspect_ratio": aspect_ratio,
                "prompt": prompt,
                "caption": result.get('caption', ''),
                "full_caption": result.get('full_caption', ''),
                "hashtags": result.get('hashtags', []),
                "emoji": result.get('emoji', ''),
                "call_to_action": result.get('call_to_action', '')
            }, status=status.HTTP_200_OK)
        else:
            error_message = result.get('message', 'Failed to generate poster')
            logger.error(f"Poster generation failed: {error_message}")
            return Response({
                "success": False,
                "error": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_poster endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def edit_poster(request):
    """
    POST /api/ai-poster/edit_poster/
    Generate edited poster using prompt + uploaded image
    
    Form data:
    - prompt: Text description for the edit
    - image: Uploaded image file
    - aspect_ratio: Optional (1:1, 16:9, 4:5)
    """
    try:
        prompt = request.data.get('prompt')
        aspect_ratio = request.data.get('aspect_ratio', '1:1')
        image_file = request.FILES.get('image')
        
        if not prompt:
            return Response({
                "success": False,
                "error": "Prompt is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not image_file:
            return Response({
                "success": False,
                "error": "Image file is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate aspect ratio
        valid_ratios = ['1:1', '16:9', '4:5']
        if aspect_ratio not in valid_ratios:
            aspect_ratio = '1:1'
        
        # Save uploaded image temporarily
        timestamp = int(time.time())
        temp_filename = f"temp_upload_{timestamp}_{image_file.name}"
        temp_path = f"temp_uploads/{temp_filename}"
        
        saved_path = default_storage.save(temp_path, ContentFile(image_file.read()))
        
        logger.info(f"Editing poster with prompt: {prompt[:50]}...")
        
        try:
            # Generate edited poster using AI service
            result = ai_poster_service.generate_with_image(prompt, saved_path, aspect_ratio)
            
            if result.get('status') == 'success':
                return Response({
                    "success": True,
                    "message": "Poster edited successfully",
                    "image_path": result.get('image_path'),
                    "image_url": result.get('image_url'),
                    "filename": result.get('filename'),
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "caption": result.get('caption', ''),
                    "full_caption": result.get('full_caption', ''),
                    "hashtags": result.get('hashtags', []),
                    "emoji": result.get('emoji', ''),
                    "call_to_action": result.get('call_to_action', '')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": result.get('message', 'Failed to edit poster')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        finally:
            # Clean up temporary file
            try:
                default_storage.delete(saved_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {saved_path}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in edit_poster endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def composite_poster(request):
    """
    POST /api/ai-poster/composite_poster/
    Generate composite poster combining multiple images + text prompt
    
    Form data:
    - prompt: Text description for the composite
    - images: Multiple uploaded image files
    - aspect_ratio: Optional (1:1, 16:9, 4:5)
    """
    try:
        prompt = request.data.get('prompt')
        aspect_ratio = request.data.get('aspect_ratio', '16:9')
        image_files = request.FILES.getlist('images')
        
        if not prompt:
            return Response({
                "success": False,
                "error": "Prompt is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not image_files or len(image_files) == 0:
            return Response({
                "success": False,
                "error": "At least one image file is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate aspect ratio
        valid_ratios = ['1:1', '16:9', '4:5']
        if aspect_ratio not in valid_ratios:
            aspect_ratio = '16:9'
        
        # Save uploaded images temporarily
        temp_paths = []
        timestamp = int(time.time())
        
        try:
            for i, image_file in enumerate(image_files):
                temp_filename = f"temp_composite_{timestamp}_{i}_{image_file.name}"
                temp_path = f"temp_uploads/{temp_filename}"
                saved_path = default_storage.save(temp_path, ContentFile(image_file.read()))
                temp_paths.append(saved_path)
            
            logger.info(f"Creating composite poster with {len(temp_paths)} images and prompt: {prompt[:50]}...")
            
            # Generate composite poster using AI service
            result = ai_poster_service.generate_composite(prompt, temp_paths, aspect_ratio)
            
            if result.get('status') == 'success':
                return Response({
                    "success": True,
                    "message": "Composite poster generated successfully",
                    "image_path": result.get('image_path'),
                    "image_url": result.get('image_url'),
                    "filename": result.get('filename'),
                    "aspect_ratio": aspect_ratio,
                    "prompt": prompt,
                    "images_used": len(temp_paths),
                    "caption": result.get('caption', ''),
                    "full_caption": result.get('full_caption', ''),
                    "hashtags": result.get('hashtags', []),
                    "emoji": result.get('emoji', ''),
                    "call_to_action": result.get('call_to_action', '')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "success": False,
                    "error": result.get('message', 'Failed to generate composite poster')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        finally:
            # Clean up temporary files
            for temp_path in temp_paths:
                try:
                    default_storage.delete(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {temp_path}: {str(e)}")
            
    except Exception as e:
        logger.error(f"Error in composite_poster endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def poster_service_status(request):
    """
    GET /api/ai-poster/status/
    Check AI poster service availability
    """
    try:
        is_available = ai_poster_service.is_available()
        
        return Response({
            "success": True,
            "service_available": is_available,
            "message": "AI poster service is available" if is_available else "AI poster service is not available"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error checking poster service status: {str(e)}")
        return Response({
            "success": False,
            "service_available": False,
            "error": "Failed to check service status"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def add_text_overlay(request):
    """
    POST /api/ai/ai-poster/add_text_overlay/
    Add text overlay to an uploaded textile image
    
    Form data:
    - image: Uploaded textile image file
    - text_prompt: Text to add to the image
    - text_style: Optional text style (elegant, bold, modern, vintage)
    """
    try:
        # Get uploaded image
        if 'image' not in request.FILES:
            return Response({
                "success": False,
                "error": "Image file is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image_file = request.FILES['image']
        text_prompt = request.data.get('text_prompt', '')
        text_style = request.data.get('text_style', 'elegant')
        
        if not text_prompt:
            return Response({
                "success": False,
                "error": "Text prompt is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate text style
        valid_styles = ['elegant', 'bold', 'modern', 'vintage']
        if text_style not in valid_styles:
            text_style = 'elegant'
        
        logger.info(f"Adding text overlay with prompt: {text_prompt[:50]}...")
        
        # Check if service is available first
        if not ai_poster_service.is_available():
            return Response({
                "success": False,
                "error": "AI poster service is not available. Please check configuration."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Save uploaded image temporarily
        import uuid
        temp_filename = f"temp_{uuid.uuid4().hex}_{image_file.name}"
        temp_path = default_storage.save(f"temp_images/{temp_filename}", ContentFile(image_file.read()))
        full_temp_path = default_storage.path(temp_path)
        
        try:
            # Add text overlay using AI service
            result = ai_poster_service.add_text_overlay(full_temp_path, text_prompt, text_style)
            
            if result.get('status') == 'success':
                return Response({
                    "success": True,
                    "message": "Text overlay added successfully",
                    "image_path": result.get('image_path'),
                    "image_url": result.get('image_url'),
                    "filename": result.get('filename'),
                    "text_added": result.get('text_added'),
                    "style": result.get('style'),
                    "caption": result.get('caption', ''),
                    "full_caption": result.get('full_caption', ''),
                    "hashtags": result.get('hashtags', []),
                    "emoji": result.get('emoji', ''),
                    "call_to_action": result.get('call_to_action', '')
                }, status=status.HTTP_200_OK)
            else:
                error_message = result.get('message', 'Failed to add text overlay')
                logger.error(f"Text overlay failed: {error_message}")
                return Response({
                    "success": False,
                    "error": error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        finally:
            # Clean up temporary file
            try:
                if os.path.exists(full_temp_path):
                    os.remove(full_temp_path)
                default_storage.delete(temp_path)
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file: {str(cleanup_error)}")
            
    except Exception as e:
        logger.error(f"Error in add_text_overlay: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
