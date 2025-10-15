"""
AI Poster Generation Service using Google Gemini 2.5 Flash
Clean, production-ready implementation for textile poster generation
"""
import os
import logging
import time
import uuid
from typing import Dict, List, Any, Optional
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .ai_caption_service import AICaptionService
from .brand_overlay_service import BrandOverlayService

# Import Google GenAI
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    logging.error("Google GenAI not available. Please install: pip install google-genai")
    genai = None
    types = None
    GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class AIPosterService:
    """Service class for AI poster generation using Gemini 2.5 Flash"""
    
    def __init__(self):
        """Initialize the AI poster service"""
        self.api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.client = None
        self.caption_service = AICaptionService()
        self.brand_overlay_service = BrandOverlayService()
        
        if not GENAI_AVAILABLE:
            logger.error("Google GenAI library not available")
            return
            
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not configured")
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def generate_from_prompt(self, prompt: str, aspect_ratio: str = "1:1", user=None) -> Dict[str, Any]:
        """
        Generate poster image from text prompt only
        
        Args:
            prompt: Text description for the poster
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating poster from prompt: {prompt[:50]}...")
            
            # Try multiple prompt variations if the first one fails
            prompts_to_try = [
                prompt,
                f"Create a high-quality image: {prompt}",
                f"Generate a professional image: {prompt}",
                f"Design an image: {prompt}"
            ]
            
            for attempt, current_prompt in enumerate(prompts_to_try):
                logger.info(f"Attempt {attempt + 1}: Trying prompt: {current_prompt[:50]}...")
                
                # Configure image generation
                image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
                
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[current_prompt],
                    config=types.GenerateContentConfig(
                        response_modalities=['Image'],
                        image_config=image_config,
                    ),
                )
            
                # Process response and save image
                if not response.candidates or len(response.candidates) == 0:
                    logger.warning(f"Attempt {attempt + 1}: No candidates returned from Gemini model")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No candidates returned from model"}
                
                candidate = response.candidates[0]
                logger.info(f"Attempt {attempt + 1}: Gemini response candidate: {candidate}")
                
                if not candidate.content:
                    logger.warning(f"Attempt {attempt + 1}: No content in Gemini response candidate")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No content returned from model"}
                
                if not candidate.content.parts:
                    logger.warning(f"Attempt {attempt + 1}: No content parts in Gemini response")
                    logger.warning(f"Content object: {candidate.content}")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No content parts returned from model"}
                
                logger.info(f"Attempt {attempt + 1}: Found {len(candidate.content.parts)} content parts")
                
                # Try to process the image
                image_processed = False
                for part in candidate.content.parts:
                    if hasattr(part, 'inline_data') and part.inline_data is not None:
                        try:
                            image = Image.open(BytesIO(part.inline_data.data))
                            
                            # Generate unique filename
                            timestamp = int(time.time())
                            filename = f"generated_poster_{timestamp}.png"
                            output_path = f"generated_posters/{filename}"
                            
                            # Save to media storage
                            image_bytes = BytesIO()
                            image.save(image_bytes, format='PNG')
                            image_bytes.seek(0)
                            
                            saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                            image_url = default_storage.url(saved_path)
                            # Ensure full URL for download
                            if not image_url.startswith('http'):
                                image_url = f"http://localhost:8000{image_url}"
                            
                            logger.info(f"Poster generated successfully on attempt {attempt + 1}: {saved_path}")
                            
                            # Generate caption and hashtags for the poster
                            caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                            
                            # Add brand overlay if user has company profile
                            final_result = {
                                "status": "success", 
                                "image_path": saved_path,
                                "image_url": image_url,
                                "filename": filename,
                                "caption": caption_result.get("caption", ""),
                                "full_caption": caption_result.get("full_caption", ""),
                                "hashtags": caption_result.get("hashtags", []),
                                "emoji": caption_result.get("emoji", ""),
                                "call_to_action": caption_result.get("call_to_action", ""),
                                "branding_applied": False
                            }
                            
                            # Apply brand overlay if user is provided and has company profile
                            if user:
                                try:
                                    from users.models import CompanyProfile
                                    company_profile = getattr(user, 'company_profile', None)
                                    if company_profile and company_profile.has_complete_profile:
                                        brand_result = self.brand_overlay_service.create_branded_poster(
                                            saved_path, company_profile
                                        )
                                        if brand_result.get('status') == 'success':
                                            final_result.update({
                                                "image_path": brand_result.get("image_path", saved_path),
                                                "image_url": brand_result.get("image_url", image_url),
                                                "filename": brand_result.get("filename", filename),
                                                "branding_applied": True,
                                                "logo_added": brand_result.get("logo_added", False),
                                                "contact_info_added": brand_result.get("contact_info_added", False)
                                            })
                                        else:
                                            logger.warning(f"Brand overlay failed: {brand_result.get('message')}")
                                except Exception as brand_error:
                                    logger.warning(f"Brand overlay error: {str(brand_error)}")
                            
                            return final_result
                        except Exception as img_error:
                            logger.error(f"Error processing image: {str(img_error)}")
                            continue
                
                if not image_processed:
                    logger.warning(f"Attempt {attempt + 1}: No valid image data found in response")
                    if attempt < len(prompts_to_try) - 1:
                        continue
                    return {"status": "error", "message": "No valid image data found in response"}
            
            return {"status": "error", "message": "All prompt attempts failed"}
            
        except Exception as e:
            logger.error(f"Error generating poster from prompt: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_with_image(self, prompt: str, image_path: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
        """
        Generate edited poster using prompt + uploaded image
        
        Args:
            prompt: Text description for the edit
            image_path: Path to uploaded image (Django storage path)
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating edited poster with prompt: {prompt[:50]}...")
            
            # Load and prepare image from Django storage
            try:
                # Try to get the file from Django storage
                with default_storage.open(image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as storage_error:
                logger.error(f"Failed to open image from storage: {str(storage_error)}")
                # Fallback: try direct file system access
                try:
                    full_path = default_storage.path(image_path)
                    with open(full_path, "rb") as f:
                        image_data = f.read()
                except Exception as fs_error:
                    logger.error(f"Failed to open image from file system: {str(fs_error)}")
                    return {"status": "error", "message": f"Failed to load image: {str(fs_error)}"}
            
            # Create image part
            image_part = types.Part(
                inline_data=types.Blob(
                    data=image_data,
                    mime_type="image/jpeg"
                )
            )
            
            # Configure image generation
            image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[image_part, prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],
                    image_config=image_config,
                ),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    edited_image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"edited_poster_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Save to media storage
                    image_bytes = BytesIO()
                    edited_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    logger.info(f"Edited poster generated successfully: {saved_path}")
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", "")
                    }
            
            return {"status": "error", "message": "No edited image returned from model"}
            
        except Exception as e:
            logger.error(f"Error generating edited poster: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_composite(self, prompt: str, image_paths: List[str], aspect_ratio: str = "16:9") -> Dict[str, Any]:
        """
        Generate composite poster combining multiple images + text prompt
        
        Args:
            prompt: Text description for the composite
            image_paths: List of image file paths
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating composite poster with {len(image_paths)} images and prompt: {prompt[:50]}...")
            
            # Load all images
            image_parts = []
            for image_path in image_paths:
                try:
                    # Try to get the file from Django storage first
                    try:
                        with default_storage.open(image_path, 'rb') as f:
                            image_data = f.read()
                    except Exception as storage_error:
                        logger.warning(f"Failed to open image from storage: {str(storage_error)}")
                        # Fallback: try direct file system access
                        full_path = default_storage.path(image_path)
                        with open(full_path, "rb") as f:
                            image_data = f.read()
                    
                    image_part = types.Part(
                        inline_data=types.Blob(
                            data=image_data,
                            mime_type="image/jpeg"
                        )
                    )
                    image_parts.append(image_part)
                except Exception as e:
                    logger.warning(f"Failed to load image {image_path}: {str(e)}")
                    continue
            
            if not image_parts:
                return {"status": "error", "message": "No valid images provided"}
            
            # Add text prompt
            contents = image_parts + [prompt]
            
            # Configure image generation
            image_config = types.ImageConfig(aspect_ratio=aspect_ratio)
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],
                    image_config=image_config,
                ),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    composite_image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"composite_poster_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Save to media storage
                    image_bytes = BytesIO()
                    composite_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    logger.info(f"Composite poster generated successfully: {saved_path}")
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(prompt, image_url)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", "")
                    }
            
            return {"status": "error", "message": "No composite image returned"}
            
        except Exception as e:
            logger.error(f"Error generating composite poster: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def add_text_overlay(self, image_path: str, text_prompt: str, text_style: str = "elegant") -> Dict[str, Any]:
        """
        Add text overlay to an existing textile image using AI
        
        Args:
            image_path: Path to the uploaded textile image
            text_prompt: Text to add to the image
            text_style: Style of the text (elegant, bold, modern, vintage)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Adding text overlay to image with prompt: {text_prompt[:50]}...")
            
            # Load and prepare image from Django storage
            try:
                # Try to get the file from Django storage
                with default_storage.open(image_path, 'rb') as f:
                    image_data = f.read()
            except Exception as storage_error:
                logger.error(f"Failed to open image from storage: {str(storage_error)}")
                # Fallback: try direct file system access
                try:
                    full_path = default_storage.path(image_path)
                    with open(full_path, "rb") as f:
                        image_data = f.read()
                except Exception as fs_error:
                    logger.error(f"Failed to open image from file system: {str(fs_error)}")
                    return {"status": "error", "message": f"Failed to load image: {str(fs_error)}"}
            
            # Create image part
            image_part = types.Part(
                inline_data=types.Blob(
                    data=image_data,
                    mime_type="image/jpeg"
                )
            )
            
            # Create enhanced prompt for text overlay
            enhanced_prompt = f"""
            Add the following text to this textile image: "{text_prompt}"
            
            Style requirements:
            - Text style: {text_style}
            - Make the text clearly visible and readable
            - Position the text appropriately on the textile
            - Use colors that complement the textile design
            - Ensure the text enhances the overall design
            - Maintain the textile's aesthetic appeal
            """
            
            # Configure image generation
            image_config = types.ImageConfig(aspect_ratio="1:1")
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[image_part, enhanced_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['Image'],
                    image_config=image_config,
                ),
            )
            
            # Process response and save image
            for part in response.candidates[0].content.parts:
                if part.inline_data is not None:
                    edited_image = Image.open(BytesIO(part.inline_data.data))
                    
                    # Generate unique filename
                    timestamp = int(time.time())
                    filename = f"text_overlay_{timestamp}.png"
                    output_path = f"generated_posters/{filename}"
                    
                    # Save to media storage
                    image_bytes = BytesIO()
                    edited_image.save(image_bytes, format='PNG')
                    image_bytes.seek(0)
                    
                    saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
                    image_url = default_storage.url(saved_path)
                    # Ensure full URL for download
                    if not image_url.startswith('http'):
                        image_url = f"http://localhost:8000{image_url}"
                    
                    logger.info(f"Text overlay added successfully: {saved_path}")
                    
                    # Generate caption and hashtags for the poster
                    caption_result = self.generate_caption_and_hashtags(text_prompt, image_url)
                    
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename,
                        "text_added": text_prompt,
                        "style": text_style,
                        "caption": caption_result.get("caption", ""),
                        "full_caption": caption_result.get("full_caption", ""),
                        "hashtags": caption_result.get("hashtags", []),
                        "emoji": caption_result.get("emoji", ""),
                        "call_to_action": caption_result.get("call_to_action", "")
                    }
            
            return {"status": "error", "message": "No edited image returned from model"}
            
        except Exception as e:
            logger.error(f"Error adding text overlay: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def generate_caption_and_hashtags(self, prompt: str, image_url: str = None) -> Dict[str, Any]:
        """
        Generate caption and hashtags for the generated poster
        
        Args:
            prompt: Original prompt used to generate the poster
            image_url: URL of the generated image (optional)
            
        Returns:
            Dict containing caption and hashtags
        """
        try:
            if not self.caption_service.client:
                return {"status": "error", "message": "Caption service not available"}
            
            logger.info(f"Generating caption and hashtags for prompt: {prompt[:50]}...")
            
            # Create enhanced content for better social media captions
            enhanced_content = f"""
            Create an engaging social media caption for a textile/fashion poster with the following description: {prompt}
            
            The caption should be:
            - Engaging and attention-grabbing
            - Perfect for Instagram, Facebook, and other social platforms
            - Include emotional appeal and storytelling
            - Mention the beauty and elegance of the textile/fashion item
            - Create desire and interest in the product
            - Be conversational and relatable
            - Include relevant fashion/beauty keywords
            """
            
            # Generate social media caption with enhanced content
            caption_result = self.caption_service.generate_social_media_caption(
                content=enhanced_content,
                platform="instagram",
                post_type="product_showcase",
                style="engaging",
                tone="friendly",
                include_hashtags=True,
                include_emoji=True,
                call_to_action=True
            )
            
            if caption_result.get("status") == "success":
                caption_data = caption_result.get("caption", {})
                
                # Extract hashtags from the caption
                hashtags = []
                if "hashtags" in caption_data:
                    hashtags = caption_data["hashtags"]
                elif "full_caption" in caption_data:
                    # Extract hashtags from full caption
                    import re
                    hashtag_matches = re.findall(r'#\w+', caption_data["full_caption"])
                    hashtags = list(set(hashtag_matches))  # Remove duplicates
                
                # Generate additional textile-specific hashtags
                textile_hashtags = [
                    "#textile", "#fashion", "#design", "#style", "#trendy",
                    "#handmade", "#artisan", "#craft", "#beautiful", "#elegant"
                ]
                
                # Combine hashtags and remove duplicates
                all_hashtags = list(set(hashtags + textile_hashtags))
                
                logger.info(f"Caption and hashtags generated successfully")
                return {
                    "status": "success",
                    "caption": caption_data.get("main_text", ""),
                    "full_caption": caption_data.get("full_caption", ""),
                    "hashtags": all_hashtags[:15],  # Limit to 15 hashtags
                    "emoji": caption_data.get("emoji", ""),
                    "call_to_action": caption_data.get("call_to_action", "")
                }
            else:
                logger.warning(f"Caption generation failed: {caption_result.get('message', 'Unknown error')}")
                # Create more meaningful fallback captions
                fallback_captions = [
                    f"✨ Discover the elegance of {prompt[:40]}... Perfect for making a statement! ✨",
                    f"🌟 Elevate your style with this stunning {prompt[:40]}... A must-have for your wardrobe! 🌟",
                    f"💫 Fall in love with this gorgeous {prompt[:40]}... Timeless beauty meets modern elegance! 💫",
                    f"🌸 Embrace the beauty of {prompt[:40]}... Where tradition meets contemporary fashion! 🌸"
                ]
                
                import random
                selected_caption = random.choice(fallback_captions)
                
                return {
                    "status": "success",
                    "caption": selected_caption,
                    "full_caption": f"{selected_caption}\n\n✨ Perfect for special occasions, festivals, or everyday elegance ✨\n\n💫 Handcrafted with love and attention to detail 💫\n\n🌸 Available now - don't miss out on this beauty! 🌸",
                    "hashtags": ["#fashion", "#style", "#elegant", "#beautiful", "#textile", "#design", "#trendy", "#outfit", "#fashionista", "#styleinspo", "#ootd", "#fashionblogger", "#stylegoals", "#fashionlover", "#styletips"],
                    "emoji": "✨",
                    "call_to_action": "✨ Shop now and elevate your style! ✨"
                }
                
        except Exception as e:
            logger.error(f"Error generating caption and hashtags: {str(e)}")
            # Create meaningful fallback even for exceptions
            fallback_captions = [
                f"✨ Discover the elegance of {prompt[:40]}... Perfect for making a statement! ✨",
                f"🌟 Elevate your style with this stunning {prompt[:40]}... A must-have for your wardrobe! 🌟",
                f"💫 Fall in love with this gorgeous {prompt[:40]}... Timeless beauty meets modern elegance! 💫"
            ]
            
            import random
            selected_caption = random.choice(fallback_captions)
            
            return {
                "status": "success",
                "caption": selected_caption,
                "full_caption": f"{selected_caption}\n\n✨ Perfect for special occasions, festivals, or everyday elegance ✨\n\n💫 Handcrafted with love and attention to detail 💫\n\n🌸 Available now - don't miss out on this beauty! 🌸",
                "hashtags": ["#fashion", "#style", "#elegant", "#beautiful", "#textile", "#design", "#trendy", "#outfit", "#fashionista", "#styleinspo", "#ootd", "#fashionblogger", "#stylegoals", "#fashionlover", "#styletips"],
                "emoji": "✨",
                "call_to_action": "✨ Shop now and elevate your style! ✨"
            }
    
    def is_available(self) -> bool:
        """Check if the AI poster service is available"""
        return self.client is not None and self.api_key is not None
