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
    
    def generate_from_prompt(self, prompt: str, aspect_ratio: str = "1:1") -> Dict[str, Any]:
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
                            
                            logger.info(f"Poster generated successfully on attempt {attempt + 1}: {saved_path}")
                            return {
                                "status": "success", 
                                "image_path": saved_path,
                                "image_url": image_url,
                                "filename": filename
                            }
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
            image_path: Path to uploaded image
            aspect_ratio: Image aspect ratio (1:1, 16:9, 4:5)
            
        Returns:
            Dict containing status and image path
        """
        try:
            if not self.client:
                return {"status": "error", "message": "Gemini client not available"}
            
            logger.info(f"Generating edited poster with prompt: {prompt[:50]}...")
            
            # Load and prepare image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
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
                    
                    logger.info(f"Edited poster generated successfully: {saved_path}")
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename
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
                    with open(image_path, "rb") as f:
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
                    
                    logger.info(f"Composite poster generated successfully: {saved_path}")
                    return {
                        "status": "success", 
                        "image_path": saved_path,
                        "image_url": image_url,
                        "filename": filename
                    }
            
            return {"status": "error", "message": "No composite image returned"}
            
        except Exception as e:
            logger.error(f"Error generating composite poster: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def is_available(self) -> bool:
        """Check if the AI poster service is available"""
        return self.client is not None and self.api_key is not None
