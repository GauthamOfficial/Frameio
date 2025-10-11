"""
AI Post Generation Views
API endpoints for AI post generation functionality
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
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
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        prompt = request.data.get('prompt')
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional parameters
        post_type = request.data.get('post_type', 'social_media')
        style = request.data.get('style', 'modern')
        tone = request.data.get('tone', 'professional')
        length = request.data.get('length', 'medium')
        include_hashtags = request.data.get('include_hashtags', True)
        include_emoji = request.data.get('include_emoji', True)
        generate_images = request.data.get('generate_images', False)
        image_style = request.data.get('image_style', 'photorealistic')
        image_quality = request.data.get('image_quality', 'high')
        target_audience = request.data.get('target_audience')
        call_to_action = request.data.get('call_to_action')
        
        try:
            # Create AI generation request record
            provider, created = AIProvider.objects.get_or_create(
                name='gemini',
                defaults={'is_active': True}
            )
            
            ai_request = AIGenerationRequest.objects.create(
                organization=organization,
                user=request.user,
                provider=provider,
                generation_type='text_generation',
                prompt=prompt,
                parameters={
                    'post_type': post_type,
                    'style': style,
                    'tone': tone,
                    'length': length,
                    'include_hashtags': include_hashtags,
                    'include_emoji': include_emoji
                }
            )
            
            # Optionally enrich prompt with targeting and CTA
            enriched_prompt = prompt
            details = []
            if target_audience:
                details.append(f"Target audience: {target_audience}")
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
            
            if result.get('success'):
                # Update the request with results
                ai_request.mark_completed(
                    result_data=result.get('content', {}),
                    result_text=result.get('content', {}).get('main_content', '')
                )
                ai_request.cost = result.get('cost', 0)
                ai_request.save(update_fields=['cost'])
                
                content = result.get('content', {})
                return Response({
                    "success": True,
                    "content": content,
                    "generated_images": content.get('generated_images', []),
                    "image_urls": content.get('image_urls', []),
                    "request_id": str(ai_request.id),
                    "metadata": {
                        "generated_at": ai_request.completed_at.isoformat() if ai_request.completed_at else None,
                        "processing_time": ai_request.processing_time,
                        "cost": float(ai_request.cost) if ai_request.cost else 0,
                        "post_type": post_type,
                        "style": style,
                        "tone": tone
                    }
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed("Post generation failed")
                return Response({
                    "success": False,
                    "error": "Post generation failed"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Text post generation failed: {str(e)}")
            return Response(
                {"error": f"Text post generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_image_post(self, request):
        """Generate AI post content with images"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        prompt = request.data.get('prompt')
        images = request.FILES.getlist('images')
        
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not images:
            return Response(
                {"error": "At least one image is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get optional parameters
        post_type = request.data.get('post_type', 'social_media')
        style = request.data.get('style', 'modern')
        tone = request.data.get('tone', 'professional')
        
        try:
            # Save uploaded images temporarily
            image_paths = []
            for image in images:
                # Generate unique filename
                filename = f"temp_{uuid.uuid4().hex}_{image.name}"
                file_path = default_storage.save(f"temp_images/{filename}", ContentFile(image.read()))
                image_paths.append(default_storage.path(file_path))
            
            # Create AI generation request record
            provider, created = AIProvider.objects.get_or_create(
                name='gemini',
                defaults={'is_active': True}
            )
            
            ai_request = AIGenerationRequest.objects.create(
                organization=organization,
                user=request.user,
                provider=provider,
                generation_type='text_generation',
                prompt=prompt,
                parameters={
                    'post_type': post_type,
                    'style': style,
                    'tone': tone,
                    'image_count': len(images)
                }
            )
            
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
                        os.remove(image_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {image_path}: {str(e)}")
            
            if result.get('success'):
                # Update the request with results
                ai_request.mark_completed(
                    result_data=result.get('content', {}),
                    result_text=result.get('content', {}).get('main_content', '')
                )
                ai_request.cost = result.get('cost', 0)
                ai_request.save(update_fields=['cost'])
                
                content = result.get('content', {})
                return Response({
                    "success": True,
                    "content": content,
                    "generated_images": content.get('generated_images', []),
                    "image_urls": content.get('image_urls', []),
                    "request_id": str(ai_request.id),
                    "metadata": {
                        "generated_at": ai_request.completed_at.isoformat() if ai_request.completed_at else None,
                        "processing_time": ai_request.processing_time,
                        "cost": float(ai_request.cost) if ai_request.cost else 0,
                        "post_type": post_type,
                        "style": style,
                        "tone": tone,
                        "image_count": len(images)
                    }
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed("Image post generation failed")
                return Response({
                    "success": False,
                    "error": "Image post generation failed"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Image post generation failed: {str(e)}")
            return Response(
                {"error": f"Image post generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def generate_social_media_post(self, request):
        """Generate optimized social media post content"""
        organization = get_current_organization()
        if not organization:
            return Response(
                {"error": "Organization context required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate required fields
        prompt = request.data.get('prompt')
        platform = request.data.get('platform', 'instagram')  # instagram, facebook, twitter, linkedin
        target_audience = request.data.get('target_audience')
        call_to_action = request.data.get('call_to_action')
        
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Platform-specific parameters
        platform_configs = {
            'instagram': {
                'post_type': 'social_media',
                'style': 'modern',
                'tone': 'friendly',
                'length': 'medium',
                'include_hashtags': True,
                'include_emoji': True
            },
            'facebook': {
                'post_type': 'social_media',
                'style': 'casual',
                'tone': 'conversational',
                'length': 'medium',
                'include_hashtags': True,
                'include_emoji': True
            },
            'twitter': {
                'post_type': 'social_media',
                'style': 'modern',
                'tone': 'conversational',
                'length': 'short',
                'include_hashtags': True,
                'include_emoji': True
            },
            'linkedin': {
                'post_type': 'social_media',
                'style': 'professional',
                'tone': 'professional',
                'length': 'medium',
                'include_hashtags': True,
                'include_emoji': False
            }
        }
        
        config = platform_configs.get(platform, platform_configs['instagram'])
        
        try:
            # Create AI generation request record
            provider, created = AIProvider.objects.get_or_create(
                name='gemini',
                defaults={'is_active': True}
            )
            
            ai_request = AIGenerationRequest.objects.create(
                organization=organization,
                user=request.user,
                provider=provider,
                generation_type='text_generation',
                prompt=prompt,
                parameters={
                    'platform': platform,
                    **config
                }
            )
            
            # Optional image generation parameters
            generate_images = request.data.get('generate_images', False)
            image_style = request.data.get('image_style', 'photorealistic')
            image_quality = request.data.get('image_quality', 'high')

            # Optionally enrich prompt with targeting and CTA
            enriched_prompt = prompt
            details = []
            if target_audience:
                details.append(f"Target audience: {target_audience}")
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
            
            if result.get('success'):
                # Update the request with results
                ai_request.mark_completed(
                    result_data=result.get('content', {}),
                    result_text=result.get('content', {}).get('main_content', '')
                )
                ai_request.cost = result.get('cost', 0)
                ai_request.save(update_fields=['cost'])
                
                return Response({
                    "success": True,
                    "content": result.get('content', {}),
                    "generated_images": result.get('content', {}).get('generated_images', []),
                    "image_urls": result.get('content', {}).get('image_urls', []),
                    "platform": platform,
                    "request_id": str(ai_request.id),
                    "metadata": {
                        "generated_at": ai_request.completed_at.isoformat() if ai_request.completed_at else None,
                        "processing_time": ai_request.processing_time,
                        "cost": float(ai_request.cost) if ai_request.cost else 0,
                        "platform": platform,
                        "engagement_score": result.get('content', {}).get('engagement_score', 0)
                    }
                }, status=status.HTTP_200_OK)
            else:
                ai_request.mark_failed("Social media post generation failed")
                return Response({
                    "success": False,
                    "error": "Social media post generation failed"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"Social media post generation failed: {str(e)}")
            return Response(
                {"error": f"Social media post generation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def get_post_templates(self, request):
        """Get available post templates"""
        templates = [
            {
                'id': 'social_media_general',
                'name': 'General Social Media Post',
                'description': 'Versatile post for any social media platform',
                'post_type': 'social_media',
                'style': 'modern',
                'tone': 'friendly',
                'length': 'medium'
            },
            {
                'id': 'instagram_lifestyle',
                'name': 'Instagram Lifestyle Post',
                'description': 'Engaging post optimized for Instagram',
                'post_type': 'social_media',
                'style': 'modern',
                'tone': 'friendly',
                'length': 'medium'
            },
            {
                'id': 'linkedin_professional',
                'name': 'LinkedIn Professional Post',
                'description': 'Professional post for LinkedIn',
                'post_type': 'social_media',
                'style': 'professional',
                'tone': 'professional',
                'length': 'medium'
            },
            {
                'id': 'twitter_quick',
                'name': 'Twitter Quick Post',
                'description': 'Short, punchy post for Twitter',
                'post_type': 'social_media',
                'style': 'modern',
                'tone': 'conversational',
                'length': 'short'
            },
            {
                'id': 'blog_article',
                'name': 'Blog Article',
                'description': 'Comprehensive blog post content',
                'post_type': 'blog',
                'style': 'professional',
                'tone': 'authoritative',
                'length': 'long'
            },
            {
                'id': 'announcement',
                'name': 'Announcement Post',
                'description': 'Formal announcement post',
                'post_type': 'announcement',
                'style': 'formal',
                'tone': 'authoritative',
                'length': 'medium'
            }
        ]
        
        return Response({
            "success": True,
            "templates": templates
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def get_service_status(self, request):
        """Get AI post generation service status"""
        is_available = self.caption_service.is_available() and self.poster_service.is_available()
        
        return Response({
            "success": True,
            "service_available": is_available,
            "fallback_mode": not is_available,
            "service_name": "AI Post Generation Service",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)
