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
from .models import GeneratedPoster

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
        
        # Validate aspect ratio (broaden supported list)
        valid_ratios = ['1:1', '16:9', '9:16', '4:5', '5:4', '3:2', '2:3']
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
        user = getattr(request, 'user', None) if hasattr(request, 'user') else None
        
        # Enhanced debugging for user context
        logger.info(f"=== POSTER GENERATION DEBUG ===")
        logger.info(f"Request user: {user}")
        logger.info(f"User authenticated: {hasattr(request, 'user') and request.user.is_authenticated}")
        logger.info(f"Request headers: {dict(request.META)}")
        
        # Check for authentication headers
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        logger.info(f"Authorization header: {auth_header}")
        
        # Try to get user from different authentication methods
        if not user or not user.is_authenticated:
            logger.warning("No authenticated user found - trying fallback methods")
            
            # Check if we can get user from development headers
            dev_user_id = request.META.get('HTTP_X_DEV_USER_ID')
            if dev_user_id:
                try:
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    user = User.objects.get(id=dev_user_id)
                    logger.info(f"Found user from development headers: {user}")
                except Exception as e:
                    logger.error(f"Failed to get user from dev headers: {e}")
            
            # Fallback: Try to get the first user with a complete company profile
            if not user:
                try:
                    from users.models import CompanyProfile
                    from django.contrib.auth import get_user_model
                    User = get_user_model()
                    
                    # Get the first user with a complete company profile
                    company_profiles = CompanyProfile.objects.filter(
                        logo__isnull=False,
                        company_name__isnull=False
                    ).exclude(company_name='').exclude(logo='')
                    
                    if company_profiles.exists():
                        user = company_profiles.first().user
                        logger.info(f"Using fallback user with complete profile: {user.username}")
                    else:
                        logger.warning("No users with complete company profiles found")
                except Exception as e:
                    logger.error(f"Error in fallback user selection: {e}")
        else:
            logger.info(f"Authenticated user found: {user.username} ({user.email})")
            
            # Check if user has company profile
            try:
                from users.models import CompanyProfile
                company_profile = getattr(user, 'company_profile', None)
                if company_profile:
                    logger.info(f"Company profile found: {company_profile.company_name}")
                    logger.info(f"Has logo: {bool(company_profile.logo)}")
                    logger.info(f"Has contact info: {bool(company_profile.get_contact_info())}")
                    logger.info(f"Profile complete: {company_profile.has_complete_profile}")
                else:
                    logger.warning("No company profile found for user")
            except Exception as e:
                logger.error(f"Error checking company profile: {e}")
        
        # Pass request context to service for proper URL generation
        ai_poster_service._request = request
        result = ai_poster_service.generate_from_prompt(prompt, aspect_ratio, user)
        
        if result.get('status') == 'success':
            # Get organization from user if available
            organization = None
            if user and hasattr(user, 'organization'):
                organization = user.organization
            elif user:
                # Try to get organization from user's company profile
                try:
                    from users.models import CompanyProfile
                    company_profile = getattr(user, 'company_profile', None)
                    if company_profile and hasattr(company_profile, 'organization'):
                        organization = company_profile.organization
                except Exception as e:
                    logger.warning(f"Could not get organization: {e}")
            
            # Save the generated poster to database
            try:
                poster = GeneratedPoster.objects.create(
                    organization=organization,
                    user=user,
                    image_url=result.get('image_url', ''),
                    image_path=result.get('image_path', ''),
                    caption=result.get('caption', ''),
                    full_caption=result.get('full_caption', ''),
                    prompt=prompt,
                    aspect_ratio=result.get('aspect_ratio_final', aspect_ratio),
                    width=result.get('width'),
                    height=result.get('height'),
                    hashtags=result.get('hashtags', []),
                    emoji=result.get('emoji', ''),
                    call_to_action=result.get('call_to_action', ''),
                    branding_applied=result.get('branding_applied', False),
                    logo_added=result.get('logo_added', False),
                    contact_info_added=result.get('contact_info_added', False),
                    branding_metadata=result.get('branding_metadata', {})
                )
                logger.info(f"Poster saved to database with ID: {poster.id}")
            except Exception as e:
                logger.error(f"Failed to save poster to database: {str(e)}")
                # Continue even if save fails
            
            return Response({
                "success": True,
                "message": "Poster generated successfully",
                "poster_id": str(poster.id) if 'poster' in locals() else None,
                "image_path": result.get('image_path'),
                "image_url": result.get('image_url'),
                "filename": result.get('filename'),
                "aspect_ratio": aspect_ratio,
                "width": result.get('width'),
                "height": result.get('height'),
                "aspect_ratio_final": result.get('aspect_ratio_final'),
                "prompt": prompt,
                "caption": result.get('caption', ''),
                "full_caption": result.get('full_caption', ''),
                "hashtags": result.get('hashtags', []),
                "emoji": result.get('emoji', ''),
                "call_to_action": result.get('call_to_action', ''),
                "branding_applied": result.get('branding_applied', False),
                "logo_added": result.get('logo_added', False),
                "contact_info_added": result.get('contact_info_added', False),
                "branding_metadata": result.get('branding_metadata', {})
            }, status=status.HTTP_200_OK)
        else:
            error_message = result.get('message', 'Failed to generate poster')
            logger.error(f"Poster generation failed: {error_message}")
            return Response({
                "success": False,
                "error": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in generate_poster endpoint: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        error_message = str(e) if settings.DEBUG else "Internal server error"
        try:
            response = Response({
                "success": False,
                "error": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response['Content-Type'] = 'application/json'
            return response
        except Exception as response_error:
            logger.error(f"Failed to create error response: {str(response_error)}")
            from django.http import JsonResponse
            return JsonResponse({
                "success": False,
                "error": "Internal server error"
            }, status=500)


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
    saved_path = None
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
        
        # Validate aspect ratio (broaden supported list)
        valid_ratios = ['1:1', '16:9', '9:16', '4:5', '5:4', '3:2', '2:3']
        if aspect_ratio not in valid_ratios:
            aspect_ratio = '1:1'
        
        # Save uploaded image temporarily
        timestamp = int(time.time())
        temp_filename = f"temp_upload_{timestamp}_{image_file.name}"
        temp_path = f"temp_uploads/{temp_filename}"
        
        try:
            saved_path = default_storage.save(temp_path, ContentFile(image_file.read()))
        except Exception as save_error:
            logger.error(f"Failed to save uploaded image: {str(save_error)}")
            import traceback
            logger.error(traceback.format_exc())
            return Response({
                "success": False,
                "error": f"Failed to save uploaded image: {str(save_error)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        logger.info(f"Editing poster with prompt: {prompt[:50]}...")
        
        # Check if service is available first
        if not ai_poster_service.is_available():
            # Clean up temp file before returning
            try:
                default_storage.delete(saved_path)
            except:
                pass
            return Response({
                "success": False,
                "error": "AI poster service is not available. Please check configuration."
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        response = None
        try:
            # Get user for branding (same logic as generate_poster)
            user = getattr(request, 'user', None) if hasattr(request, 'user') else None
            
            # Enhanced debugging for user context
            logger.info(f"=== EDIT POSTER DEBUG ===")
            logger.info(f"Request user: {user}")
            logger.info(f"User authenticated: {hasattr(request, 'user') and request.user.is_authenticated}")
            
            # Check for authentication headers
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            logger.info(f"Authorization header: {auth_header}")
            
            # Try to get user from different authentication methods
            if not user or not user.is_authenticated:
                logger.warning("No authenticated user found - trying fallback methods")
                
                # Check if we can get user from development headers
                dev_user_id = request.META.get('HTTP_X_DEV_USER_ID')
                if dev_user_id:
                    try:
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        user = User.objects.get(id=dev_user_id)
                        logger.info(f"Found user from development headers: {user}")
                    except Exception as e:
                        logger.error(f"Failed to get user from dev headers: {e}")
                
                # Fallback: Try to get the first user with a complete company profile
                if not user:
                    try:
                        from users.models import CompanyProfile
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        
                        # Get the first user with a complete company profile
                        company_profiles = CompanyProfile.objects.filter(
                            logo__isnull=False,
                            company_name__isnull=False
                        ).exclude(company_name='').exclude(logo='')
                        
                        if company_profiles.exists():
                            user = company_profiles.first().user
                            logger.info(f"Using fallback user with complete profile: {user.username}")
                        else:
                            logger.warning("No users with complete company profiles found")
                    except Exception as e:
                        logger.error(f"Error in fallback user selection: {e}")
            else:
                logger.info(f"Authenticated user found: {user.username} ({user.email})")
            
            # Generate edited poster using AI service with user for branding
            logger.info(f"Calling generate_with_image with path: {saved_path}")
            result = ai_poster_service.generate_with_image(prompt, saved_path, aspect_ratio, user)
            logger.info(f"generate_with_image returned: {result.get('status')}")
            
            if result.get('status') == 'success':
                # Get organization from user if available
                organization = None
                if user and hasattr(user, 'organization'):
                    organization = user.organization
                elif user:
                    try:
                        from users.models import CompanyProfile
                        company_profile = getattr(user, 'company_profile', None)
                        if company_profile and hasattr(company_profile, 'organization'):
                            organization = company_profile.organization
                    except Exception as e:
                        logger.warning(f"Could not get organization: {e}")
                
                # Save the edited poster to database
                poster = None
                try:
                    poster = GeneratedPoster.objects.create(
                        organization=organization,
                        user=user,
                        image_url=result.get('image_url', ''),
                        image_path=result.get('image_path', ''),
                        caption=result.get('caption', ''),
                        full_caption=result.get('full_caption', ''),
                        prompt=prompt,
                        aspect_ratio=result.get('aspect_ratio_final', aspect_ratio),
                        width=result.get('width'),
                        height=result.get('height'),
                        hashtags=result.get('hashtags', []),
                        emoji=result.get('emoji', ''),
                        call_to_action=result.get('call_to_action', ''),
                        branding_applied=result.get('branding_applied', False),
                        logo_added=result.get('logo_added', False),
                        contact_info_added=result.get('contact_info_added', False),
                        branding_metadata=result.get('branding_metadata', {})
                    )
                    logger.info(f"Edited poster saved to database with ID: {poster.id}")
                except Exception as e:
                    logger.error(f"Failed to save edited poster to database: {str(e)}")
                    # Continue even if save fails
                
                response = Response({
                    "success": True,
                    "message": "Poster edited successfully",
                    "poster_id": str(poster.id) if poster else None,
                    "image_path": result.get('image_path'),
                    "image_url": result.get('image_url'),
                    "filename": result.get('filename'),
                    "aspect_ratio": aspect_ratio,
                    "width": result.get('width'),
                    "height": result.get('height'),
                    "aspect_ratio_final": result.get('aspect_ratio_final'),
                    "prompt": prompt,
                    "caption": result.get('caption', ''),
                    "full_caption": result.get('full_caption', ''),
                    "hashtags": result.get('hashtags', []),
                    "emoji": result.get('emoji', ''),
                    "call_to_action": result.get('call_to_action', ''),
                    "branding_applied": result.get('branding_applied', False),
                    "logo_added": result.get('logo_added', False),
                    "contact_info_added": result.get('contact_info_added', False),
                    "branding_metadata": result.get('branding_metadata', {})
                }, status=status.HTTP_200_OK)
            else:
                error_message = result.get('message', 'Failed to edit poster')
                logger.error(f"Poster editing failed: {error_message}")
                response = Response({
                    "success": False,
                    "error": error_message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as inner_e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error in edit_poster inner block: {str(inner_e)}")
            logger.error(f"Traceback: {error_trace}")
            # Create error response
            response = Response({
                "success": False,
                "error": str(inner_e) if settings.DEBUG else "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        finally:
            # Clean up temporary file
            try:
                if saved_path:
                    default_storage.delete(saved_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {saved_path}: {str(e)}")
        
        # Ensure response is always set
        if response is None:
            logger.error("Response was None - creating fallback error response")
            response = Response({
                "success": False,
                "error": "Unexpected error: response was not created"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Force content type
        response['Content-Type'] = 'application/json'
        return response
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Error in edit_poster endpoint: {str(e)}")
        logger.error(f"Traceback: {error_trace}")
        
        # Clean up temp file if it exists
        if saved_path:
            try:
                default_storage.delete(saved_path)
            except:
                pass
        
        # Ensure we always return a proper JSON response
        error_message = str(e) if settings.DEBUG else "Internal server error"
        logger.error(f"Returning error response: {error_message}")
        
        try:
            response = Response({
                "success": False,
                "error": error_message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            # Force content type to ensure JSON
            response['Content-Type'] = 'application/json'
            return response
        except Exception as response_error:
            # If even Response creation fails, log it
            logger.error(f"Failed to create error response: {str(response_error)}")
            logger.error(traceback.format_exc())
            # Try one more time with minimal data
            try:
                from django.http import JsonResponse
                return JsonResponse({
                    "success": False,
                    "error": "Internal server error"
                }, status=500)
            except:
                # Last resort - return a simple text response
                from django.http import HttpResponse
                return HttpResponse('{"success": false, "error": "Internal server error"}', 
                                  status=500, content_type='application/json')


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_poster(request, poster_id):
    """
    GET /api/ai-poster/poster/<poster_id>/
    Get individual poster data for sharing
    """
    try:
        # For now, we'll return mock data since we don't have a Poster model yet
        # In a real implementation, you would query the database for the poster
        
        # Mock poster data - replace with actual database query
        poster_data = {
            "id": poster_id,
            "image_url": f"http://localhost:8000/media/generated_posters/poster_{poster_id}.png",
            "caption": "Check out this amazing AI-generated poster!",
            "full_caption": "Check out this amazing AI-generated poster! Created with cutting-edge AI technology. #AI #Poster #Design #Innovation",
            "hashtags": ["#AI", "#Poster", "#Design", "#Innovation"],
            "prompt": "Create a modern textile poster for a silk saree brand",
            "aspect_ratio": "4:5",
            "width": 1080,
            "height": 1350,
            "generated_at": "2024-01-01T00:00:00Z",
            "branding_applied": False,
            "logo_added": False,
            "contact_info_added": False
        }
        
        return Response({
            "success": True,
            "poster": poster_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in get_poster endpoint: {str(e)}")
        return Response({
            "success": False,
            "error": "Poster not found"
        }, status=status.HTTP_404_NOT_FOUND)


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
        
        # Validate aspect ratio (broaden supported list)
        valid_ratios = ['1:1', '16:9', '9:16', '4:5', '5:4', '3:2', '2:3']
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
                # Get user and organization for saving
                user = getattr(request, 'user', None) if hasattr(request, 'user') else None
                organization = None
                if user and hasattr(user, 'organization'):
                    organization = user.organization
                elif user:
                    try:
                        from users.models import CompanyProfile
                        company_profile = getattr(user, 'company_profile', None)
                        if company_profile and hasattr(company_profile, 'organization'):
                            organization = company_profile.organization
                    except Exception as e:
                        logger.warning(f"Could not get organization: {e}")
                
                # Save the generated composite poster to database
                poster = None
                try:
                    poster = GeneratedPoster.objects.create(
                        organization=organization,
                        user=user,
                        image_url=result.get('image_url', ''),
                        image_path=result.get('image_path', ''),
                        caption=result.get('caption', ''),
                        full_caption=result.get('full_caption', ''),
                        prompt=prompt,
                        aspect_ratio=result.get('aspect_ratio_final', aspect_ratio),
                        width=result.get('width'),
                        height=result.get('height'),
                        hashtags=result.get('hashtags', []),
                        emoji=result.get('emoji', ''),
                        call_to_action=result.get('call_to_action', ''),
                        branding_applied=result.get('branding_applied', False),
                        logo_added=result.get('logo_added', False),
                        contact_info_added=result.get('contact_info_added', False),
                        branding_metadata=result.get('branding_metadata', {})
                    )
                    logger.info(f"Composite poster saved to database with ID: {poster.id}")
                except Exception as e:
                    logger.error(f"Failed to save composite poster to database: {str(e)}")
                    # Continue even if save fails
                
                return Response({
                    "success": True,
                    "message": "Composite poster generated successfully",
                    "poster_id": str(poster.id) if poster else None,
                    "image_path": result.get('image_path'),
                    "image_url": result.get('image_url'),
                    "filename": result.get('filename'),
                    "aspect_ratio": aspect_ratio,
                    "width": result.get('width'),
                    "height": result.get('height'),
                    "aspect_ratio_final": result.get('aspect_ratio_final'),
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
                # Get user and organization for saving
                user = getattr(request, 'user', None) if hasattr(request, 'user') else None
                organization = None
                if user and hasattr(user, 'organization'):
                    organization = user.organization
                elif user:
                    try:
                        from users.models import CompanyProfile
                        company_profile = getattr(user, 'company_profile', None)
                        if company_profile and hasattr(company_profile, 'organization'):
                            organization = company_profile.organization
                    except Exception as e:
                        logger.warning(f"Could not get organization: {e}")
                
                # Save the poster with text overlay to database
                poster = None
                try:
                    poster = GeneratedPoster.objects.create(
                        organization=organization,
                        user=user,
                        image_url=result.get('image_url', ''),
                        image_path=result.get('image_path', ''),
                        caption=result.get('caption', ''),
                        full_caption=result.get('full_caption', ''),
                        prompt=text_prompt,  # Use text_prompt as the prompt
                        aspect_ratio=result.get('aspect_ratio', '1:1'),
                        width=result.get('width'),
                        height=result.get('height'),
                        hashtags=result.get('hashtags', []),
                        emoji=result.get('emoji', ''),
                        call_to_action=result.get('call_to_action', ''),
                        branding_applied=result.get('branding_applied', False),
                        logo_added=result.get('logo_added', False),
                        contact_info_added=result.get('contact_info_added', False),
                        branding_metadata=result.get('branding_metadata', {})
                    )
                    logger.info(f"Poster with text overlay saved to database with ID: {poster.id}")
                except Exception as e:
                    logger.error(f"Failed to save poster with text overlay to database: {str(e)}")
                    # Continue even if save fails
                
                return Response({
                    "success": True,
                    "message": "Text overlay added successfully",
                    "poster_id": str(poster.id) if poster else None,
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


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def list_posters(request):
    """
    GET /api/ai/ai-poster/posters/
    List all generated posters for the current user/organization
    
    Query params:
    - limit: Number of posters to return (default: 50)
    - offset: Offset for pagination (default: 0)
    """
    try:
        # Get user from request if authenticated
        user = None
        organization = None
        
        if request.user and request.user.is_authenticated:
            user = request.user
            # Try to get organization from user
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
        
        # Get query parameters
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        
        # Build queryset
        queryset = GeneratedPoster.objects.all()
        
        # Filter by organization if available
        if organization:
            queryset = queryset.filter(organization=organization)
        elif user:
            queryset = queryset.filter(user=user)
        
        # Order by created_at descending
        queryset = queryset.order_by('-created_at')
        
        # Apply pagination
        total_count = queryset.count()
        posters = queryset[offset:offset + limit]
        
        # Serialize posters
        posters_data = []
        for poster in posters:
            # Ensure image_url is absolute
            image_url = poster.image_url
            if image_url and not image_url.startswith('http'):
                # Convert relative URL to absolute
                if image_url.startswith('/'):
                    # Use request to build absolute URI
                    try:
                        image_url = request.build_absolute_uri(image_url)
                    except Exception:
                        # Fallback if request.build_absolute_uri fails
                        from django.conf import settings
                        base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                        image_url = f"{base_url}{image_url}"
                else:
                    # Prepend base URL for relative paths without leading slash
                    from django.conf import settings
                    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                    image_url = f"{base_url}/{image_url}"
            
            posters_data.append({
                'id': str(poster.id),
                'image_url': image_url,
                'caption': poster.caption,
                'full_caption': poster.full_caption,
                'prompt': poster.prompt,
                'aspect_ratio': poster.aspect_ratio,
                'width': poster.width,
                'height': poster.height,
                'hashtags': poster.hashtags,
                'emoji': poster.emoji,
                'call_to_action': poster.call_to_action,
                'branding_applied': poster.branding_applied,
                'logo_added': poster.logo_added,
                'contact_info_added': poster.contact_info_added,
                'created_at': poster.created_at.isoformat(),
                'updated_at': poster.updated_at.isoformat(),
            })
        
        return Response({
            "success": True,
            "count": total_count,
            "results": posters_data,
            "limit": limit,
            "offset": offset
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error listing posters: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return Response({
            "success": False,
            "error": str(e) if settings.DEBUG else "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_poster(request, poster_id):
    """
    DELETE /api/ai/ai-poster/posters/{poster_id}/
    Delete a specific poster by ID
    """
    try:
        poster = GeneratedPoster.objects.get(id=poster_id)
        
        # Check permissions (user or organization match)
        user = request.user if request.user.is_authenticated else None
        organization = None
        
        if user:
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
        if organization and poster.organization != organization:
            return Response({
                "success": False,
                "error": "Poster not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user and poster.user and poster.user != user:
            if not organization or poster.organization != organization:
                return Response({
                    "success": False,
                    "error": "Poster not found or access denied"
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Delete associated image file if it exists
        if poster.image_path:
            try:
                from django.core.files.storage import default_storage
                if default_storage.exists(poster.image_path):
                    default_storage.delete(poster.image_path)
                    logger.info(f"Deleted image file: {poster.image_path}")
            except Exception as e:
                logger.warning(f"Failed to delete image file {poster.image_path}: {str(e)}")
        
        # Delete the poster record
        poster.delete()
        logger.info(f"Deleted poster with ID: {poster_id}")
        
        return Response({
            "success": True,
            "message": "Poster deleted successfully"
        }, status=status.HTTP_200_OK)
        
    except GeneratedPoster.DoesNotExist:
        return Response({
            "success": False,
            "error": "Poster not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error deleting poster: {str(e)}")
        return Response({
            "success": False,
            "error": str(e) if settings.DEBUG else "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET'])
@permission_classes([AllowAny])
def get_poster_by_id(request, poster_id):
    """
    GET /api/ai/ai-poster/posters/{poster_id}/
    Get a specific poster by ID
    """
    try:
        poster = GeneratedPoster.objects.get(id=poster_id)
        
        # Check permissions (user or organization match)
        user = request.user if request.user.is_authenticated else None
        organization = None
        
        if user:
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
        if organization and poster.organization != organization:
            return Response({
                "success": False,
                "error": "Poster not found or access denied"
            }, status=status.HTTP_404_NOT_FOUND)
        
        if user and poster.user and poster.user != user:
            if not organization or poster.organization != organization:
                return Response({
                    "success": False,
                    "error": "Poster not found or access denied"
                }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            "success": True,
            "poster": {
                'id': str(poster.id),
                'image_url': poster.image_url,
                'caption': poster.caption,
                'full_caption': poster.full_caption,
                'prompt': poster.prompt,
                'aspect_ratio': poster.aspect_ratio,
                'width': poster.width,
                'height': poster.height,
                'hashtags': poster.hashtags,
                'emoji': poster.emoji,
                'call_to_action': poster.call_to_action,
                'branding_applied': poster.branding_applied,
                'logo_added': poster.logo_added,
                'contact_info_added': poster.contact_info_added,
                'created_at': poster.created_at.isoformat(),
                'updated_at': poster.updated_at.isoformat(),
            }
        }, status=status.HTTP_200_OK)
        
    except GeneratedPoster.DoesNotExist:
        return Response({
            "success": False,
            "error": "Poster not found"
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting poster: {str(e)}")
        return Response({
            "success": False,
            "error": str(e) if settings.DEBUG else "Internal server error"
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
