"""
AI Post Generation Views - FIXED VERSION
Updated to use the new AI poster and caption services
"""
import logging
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import os
import uuid

from .models import AIGenerationRequest, AIProvider
from .ai_poster_service import AIPosterService
from .ai_caption_service import AICaptionService
from .post_generation_serializers import AIPostGenerationSerializer
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class AIPostGenerationViewSet(viewsets.ViewSet):
    """ViewSet for AI Post Generation"""
    permission_classes = [permissions.IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.poster_service = AIPosterService()
        self.caption_service = AICaptionService()
    
    @action(detail=False, methods=['post'])
    def generate_text_post(self, request):
        """Generate AI text post content"""
        organization = get_current_organization()
        if not organization:
            return Response({
                "success": False,
                "error": "Organization not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AIPostGenerationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "success": False,
                "error": "Invalid request data",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        prompt = data.get('prompt')
        post_type = data.get('post_type', 'social_media')
        style = data.get('style', 'modern')
        tone = data.get('tone', 'professional')
        length = data.get('length', 'medium')
        include_hashtags = data.get('include_hashtags', True)
        include_emoji = data.get('include_emoji', True)
        generate_images = data.get('generate_images', False)
        image_style = data.get('image_style', 'photorealistic')
        image_quality = data.get('image_quality', 'high')
        call_to_action = data.get('call_to_action', '')
        
        # Create AI generation request
        ai_request = AIGenerationRequest.objects.create(
            organization=organization,
            user=request.user,
            prompt=prompt,
            generation_type='text_post',
            status='pending'
        )
        
        try:
            # Enrich prompt with additional details
            details = []
            if call_to_action:
                details.append(f"Call to action: {call_to_action}")
            if details:
                enriched_prompt = f"{prompt}\n" + "\n".join(details)

            # Generate post content using caption service
            result = self.caption_service.generate_social_media_caption(
                content=enriched_prompt,
                platform=post_type,
                post_type="product_showcase",
                style=style,
                tone=tone,
                include_hashtags=include_hashtags,
                include_emoji=include_emoji,
                call_to_action=True
            )
            
            if result.get('status') == 'success':
                # Update the request with results
                caption_data = result.get('caption', {})
                ai_request.mark_completed(
                    result_data=caption_data,
                    result_text=caption_data.get('main_content', '')
                )
                ai_request.cost = 0.001  # Estimated cost
                ai_request.save(update_fields=['cost'])
                
                return Response({
                    "success": True,
                    "content": caption_data,
                    "generated_images": [],
                    "generation_id": result.get('generation_id'),
                    "cost": ai_request.cost
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed(result.get('message', 'Unknown error'))
                return Response({
                    "success": False,
                    "error": result.get('message', 'Failed to generate content')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in generate_text_post: {str(e)}")
            ai_request.mark_failed(str(e))
            return Response({
                "success": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_image_post(self, request):
        """Generate AI post with images"""
        organization = get_current_organization()
        if not organization:
            return Response({
                "success": False,
                "error": "Organization not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get uploaded images
        images = request.FILES.getlist('images')
        if not images:
            return Response({
                "success": False,
                "error": "No images provided"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        prompt = request.data.get('prompt', '')
        post_type = request.data.get('post_type', 'social_media')
        style = request.data.get('style', 'modern')
        tone = request.data.get('tone', 'professional')
        
        # Create AI generation request
        ai_request = AIGenerationRequest.objects.create(
            organization=organization,
            user=request.user,
            prompt=prompt,
            generation_type='image_post',
            status='pending'
        )
        
        try:
            # Save uploaded images temporarily
            image_paths = []
            for image in images:
                filename = f"temp_{uuid.uuid4()}_{image.name}"
                path = default_storage.save(f"temp_uploads/{filename}", ContentFile(image.read()))
                image_paths.append(path)
            
            # Generate post content with images using poster service
            result = self.poster_service.generate_composite(
                prompt=prompt,
                image_paths=image_paths,
                aspect_ratio="16:9"
            )
            
            # Clean up temporary files
            for image_path in image_paths:
                try:
                    if os.path.exists(image_path):
                        default_storage.delete(image_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file {image_path}: {str(e)}")
            
            if result.get('status') == 'success':
                # Update the request with results
                ai_request.mark_completed(
                    result_data=result,
                    result_text=f"Generated composite image: {result.get('filename', '')}"
                )
                ai_request.cost = 0.002  # Estimated cost for image generation
                ai_request.save(update_fields=['cost'])
                
                return Response({
                    "success": True,
                    "content": {
                        "main_content": f"Generated composite image from {len(images)} images",
                        "image_path": result.get('image_path'),
                        "image_url": result.get('image_url'),
                        "filename": result.get('filename')
                    },
                    "generated_images": [result.get('image_url')] if result.get('image_url') else [],
                    "generation_id": result.get('filename'),
                    "cost": ai_request.cost
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed(result.get('message', 'Unknown error'))
                return Response({
                    "success": False,
                    "error": result.get('message', 'Failed to generate content')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in generate_image_post: {str(e)}")
            ai_request.mark_failed(str(e))
            return Response({
                "success": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def generate_platform_post(self, request):
        """Generate platform-specific post content"""
        organization = get_current_organization()
        if not organization:
            return Response({
                "success": False,
                "error": "Organization not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Platform-specific configuration
        platform_configs = {
            'instagram': {
                'platform': 'instagram',
                'post_type': 'product_showcase',
                'style': 'engaging',
                'tone': 'friendly',
                'include_hashtags': True,
                'include_emoji': True
            },
            'facebook': {
                'platform': 'facebook',
                'post_type': 'product_showcase',
                'style': 'professional',
                'tone': 'authoritative',
                'include_hashtags': True,
                'include_emoji': True
            },
            'linkedin': {
                'platform': 'linkedin',
                'post_type': 'educational',
                'style': 'professional',
                'tone': 'authoritative',
                'include_hashtags': False,
                'include_emoji': False
            }
        }
        
        platform = request.data.get('platform', 'instagram')
        config = platform_configs.get(platform, platform_configs['instagram'])
        
        prompt = request.data.get('prompt', '')
        call_to_action = request.data.get('call_to_action', '')
        
        # Create AI generation request
        ai_request = AIGenerationRequest.objects.create(
            organization=organization,
            user=request.user,
            prompt=prompt,
            generation_type=f'{platform}_post',
            status='pending'
        )
        
        try:
            # Enrich prompt with additional details
            details = []
            if call_to_action:
                details.append(f"Call to action: {call_to_action}")
            if details:
                enriched_prompt = f"{prompt}\n" + "\n".join(details)

            # Generate platform-specific post content using caption service
            result = self.caption_service.generate_social_media_caption(
                content=enriched_prompt,
                platform=config['platform'],
                post_type=config['post_type'],
                style=config['style'],
                tone=config['tone'],
                include_hashtags=config['include_hashtags'],
                include_emoji=config['include_emoji'],
                call_to_action=True
            )
            
            if result.get('status') == 'success':
                # Update the request with results
                caption_data = result.get('caption', {})
                ai_request.mark_completed(
                    result_data=caption_data,
                    result_text=caption_data.get('main_content', '')
                )
                ai_request.cost = 0.001  # Estimated cost
                ai_request.save(update_fields=['cost'])
                
                return Response({
                    "success": True,
                    "content": caption_data,
                    "platform": platform,
                    "generated_images": [],
                    "generation_id": result.get('generation_id'),
                    "cost": ai_request.cost
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed(result.get('message', 'Unknown error'))
                return Response({
                    "success": False,
                    "error": result.get('message', 'Failed to generate content')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error in generate_platform_post: {str(e)}")
            ai_request.mark_failed(str(e))
            return Response({
                "success": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def get_service_status(self, request):
        """Get AI post generation service status"""
        is_available = self.caption_service.is_available() and self.poster_service.is_available()
        
        return Response({
            "success": True,
            "service_available": is_available,
            "fallback_mode": not is_available,
            "message": "AI services are available" if is_available else "AI services are not available"
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_generation_history(self, request):
        """Get user's generation history"""
        organization = get_current_organization()
        if not organization:
            return Response({
                "success": False,
                "error": "Organization not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user's generation requests
        requests = AIGenerationRequest.objects.filter(
            organization=organization,
            user=request.user
        ).order_by('-created_at')[:50]  # Last 50 requests
        
        history = []
        for req in requests:
            history.append({
                "id": req.id,
                "prompt": req.prompt,
                "generation_type": req.generation_type,
                "status": req.status,
                "cost": req.cost,
                "created_at": req.created_at.isoformat(),
                "completed_at": req.completed_at.isoformat() if req.completed_at else None
            })
        
        return Response({
            "success": True,
            "history": history,
            "total_requests": len(history)
        }, status=status.HTTP_200_OK)

