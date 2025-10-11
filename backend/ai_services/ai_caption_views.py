"""
AI Caption Generation API Views
Django REST Framework views for caption generation endpoints
"""
import os
import time
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .ai_caption_service import AICaptionService

logger = logging.getLogger(__name__)

# Initialize the AI caption service
ai_caption_service = AICaptionService()


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_product_caption(request):
    """
    POST /api/ai-caption/product_caption/
    Generate product caption for textile items
    
    Body: {
        "product_name": "Silk Saree Collection",
        "product_type": "saree",
        "style": "modern",
        "tone": "professional",
        "include_hashtags": true,
        "include_emoji": true,
        "max_length": 200
    }
    """
    try:
        data = request.data
        product_name = data.get('product_name')
        product_type = data.get('product_type', 'textile')
        style = data.get('style', 'modern')
        tone = data.get('tone', 'professional')
        include_hashtags = data.get('include_hashtags', True)
        include_emoji = data.get('include_emoji', True)
        max_length = data.get('max_length', 200)
        
        if not product_name:
            return Response({
                "success": False,
                "error": "Product name is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Generating product caption for: {product_name}")
        
        # Generate caption using AI service
        result = ai_caption_service.generate_product_caption(
            product_name=product_name,
            product_type=product_type,
            style=style,
            tone=tone,
            include_hashtags=include_hashtags,
            include_emoji=include_emoji,
            max_length=max_length
        )
        
        if result.get('status') == 'success':
            return Response({
                "success": True,
                "message": "Product caption generated successfully",
                "caption": result.get('caption'),
                "product_name": result.get('product_name'),
                "product_type": result.get('product_type'),
                "style": result.get('style'),
                "tone": result.get('tone'),
                "generation_id": result.get('generation_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "error": result.get('message', 'Failed to generate caption')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_product_caption endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_social_media_caption(request):
    """
    POST /api/ai-caption/social_media_caption/
    Generate social media caption for textile content
    
    Body: {
        "content": "New silk collection launch",
        "platform": "instagram",
        "post_type": "product_showcase",
        "style": "engaging",
        "tone": "friendly",
        "include_hashtags": true,
        "include_emoji": true,
        "call_to_action": true
    }
    """
    try:
        data = request.data
        content = data.get('content')
        platform = data.get('platform', 'instagram')
        post_type = data.get('post_type', 'product_showcase')
        style = data.get('style', 'engaging')
        tone = data.get('tone', 'friendly')
        include_hashtags = data.get('include_hashtags', True)
        include_emoji = data.get('include_emoji', True)
        call_to_action = data.get('call_to_action', True)
        
        if not content:
            return Response({
                "success": False,
                "error": "Content is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Generating social media caption for {platform}")
        
        # Generate caption using AI service
        result = ai_caption_service.generate_social_media_caption(
            content=content,
            platform=platform,
            post_type=post_type,
            style=style,
            tone=tone,
            include_hashtags=include_hashtags,
            include_emoji=include_emoji,
            call_to_action=call_to_action
        )
        
        if result.get('status') == 'success':
            return Response({
                "success": True,
                "message": "Social media caption generated successfully",
                "caption": result.get('caption'),
                "platform": result.get('platform'),
                "post_type": result.get('post_type'),
                "style": result.get('style'),
                "tone": result.get('tone'),
                "generation_id": result.get('generation_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "error": result.get('message', 'Failed to generate caption')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_social_media_caption endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_image_caption(request):
    """
    POST /api/ai-caption/image_caption/
    Generate caption for textile images
    
    Body: {
        "image_description": "Beautiful silk saree with intricate embroidery",
        "caption_type": "descriptive",
        "style": "professional",
        "tone": "informative",
        "include_hashtags": false,
        "include_emoji": false
    }
    """
    try:
        data = request.data
        image_description = data.get('image_description')
        caption_type = data.get('caption_type', 'descriptive')
        style = data.get('style', 'professional')
        tone = data.get('tone', 'informative')
        include_hashtags = data.get('include_hashtags', False)
        include_emoji = data.get('include_emoji', False)
        
        if not image_description:
            return Response({
                "success": False,
                "error": "Image description is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Generating image caption for: {image_description[:50]}...")
        
        # Generate caption using AI service
        result = ai_caption_service.generate_image_caption(
            image_description=image_description,
            caption_type=caption_type,
            style=style,
            tone=tone,
            include_hashtags=include_hashtags,
            include_emoji=include_emoji
        )
        
        if result.get('status') == 'success':
            return Response({
                "success": True,
                "message": "Image caption generated successfully",
                "caption": result.get('caption'),
                "caption_type": result.get('caption_type'),
                "style": result.get('style'),
                "tone": result.get('tone'),
                "generation_id": result.get('generation_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "error": result.get('message', 'Failed to generate caption')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_image_caption endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_bulk_captions(request):
    """
    POST /api/ai-caption/bulk_captions/
    Generate multiple captions for bulk products
    
    Body: {
        "products": [
            {"name": "Silk Saree", "type": "saree"},
            {"name": "Cotton Kurta", "type": "kurta"},
            {"name": "Linen Dress", "type": "dress"}
        ],
        "caption_style": "consistent",
        "brand_voice": "professional"
    }
    """
    try:
        data = request.data
        products = data.get('products', [])
        caption_style = data.get('caption_style', 'consistent')
        brand_voice = data.get('brand_voice', 'professional')
        
        if not products or len(products) == 0:
            return Response({
                "success": False,
                "error": "Products list is required"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Generating bulk captions for {len(products)} products")
        
        # Generate captions using AI service
        result = ai_caption_service.generate_bulk_captions(
            products=products,
            caption_style=caption_style,
            brand_voice=brand_voice
        )
        
        if result.get('status') == 'success':
            return Response({
                "success": True,
                "message": "Bulk captions generated successfully",
                "captions": result.get('captions'),
                "total_products": result.get('total_products'),
                "caption_style": result.get('caption_style'),
                "brand_voice": result.get('brand_voice'),
                "generation_id": result.get('generation_id')
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": False,
                "error": result.get('message', 'Failed to generate captions')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        logger.error(f"Error in generate_bulk_captions endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def caption_service_status(request):
    """
    GET /api/ai-caption/status/
    Check AI caption service availability
    """
    try:
        is_available = ai_caption_service.is_available()
        
        return Response({
            "success": True,
            "service_available": is_available,
            "message": "AI caption service is available" if is_available else "AI caption service is not available"
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error checking caption service status: {str(e)}")
        return Response({
            "success": False,
            "service_available": False,
            "error": "Failed to check service status"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

