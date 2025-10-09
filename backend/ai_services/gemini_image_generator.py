"""
Google Gemini 2.5 Flash Image Generator
Using the new Google Genai client for proper image generation
"""
import os
import logging
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.cache import cache

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None
    types = None

logger = logging.getLogger(__name__)


class GeminiImageGenerator:
    """
    Google Gemini 2.5 Flash Image Generator using the new Google Genai client
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.client = None
        self.model_name = "gemini-2.5-flash-image"
        
        if not GEMINI_AVAILABLE:
            logger.error("Google Genai package not available. Install with: pip install google-genai")
            return
            
        if not self.api_key:
            logger.warning("Google Gemini API key not configured")
            return
            
        try:
            # Initialize the Gemini client
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        style: str = "photorealistic",
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Google Gemini 2.5 Flash Image API
        
        Args:
            prompt: Text prompt for image generation
            aspect_ratio: Aspect ratio for the image (1:1, 16:9, 9:16, etc.)
            style: Image style (photorealistic, illustration, etc.)
            num_images: Number of images to generate
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized",
                "data": None
            }
        
        # Create cache key
        cache_key = self._get_cache_key(prompt, aspect_ratio, style, num_images)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for prompt: {prompt[:50]}...")
            return cached_result
        
        try:
            # Enhance prompt based on style
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            logger.info(f"Generating image with prompt: {enhanced_prompt[:100]}...")
            start_time = time.time()
            
            # Configure generation parameters
            config = types.GenerateContentConfig(
                response_modalities=['Image'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                )
            )
            
            # Generate content
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[enhanced_prompt],
                config=config
            )
            
            processing_time = time.time() - start_time
            
            # Process the response
            result = self._process_response(response, enhanced_prompt, processing_time)
            
            # Cache the result
            cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Successfully generated image in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            error_msg = f"Gemini image generation failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def generate_text_and_image(
        self,
        prompt: str,
        image_input: Union[str, Image.Image],
        aspect_ratio: str = "1:1",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image from text and image input (image editing)
        
        Args:
            prompt: Text prompt for image generation
            image_input: Input image (path or PIL Image)
            aspect_ratio: Aspect ratio for the output image
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        if not self.client:
            return {
                "success": False,
                "error": "Gemini client not initialized",
                "data": None
            }
        
        try:
            # Load image if it's a path
            if isinstance(image_input, str):
                image = Image.open(image_input)
            else:
                image = image_input
            
            logger.info(f"Generating image with text and image input: {prompt[:50]}...")
            start_time = time.time()
            
            # Configure generation parameters
            config = types.GenerateContentConfig(
                response_modalities=['Image'],
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                )
            )
            
            # Generate content with both text and image
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, image],
                config=config
            )
            
            processing_time = time.time() - start_time
            
            # Process the response
            result = self._process_response(response, prompt, processing_time)
            
            logger.info(f"Successfully generated image with text and image input in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            error_msg = f"Gemini text and image generation failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def generate_poster(
        self,
        fabric_type: str,
        offer_text: str,
        theme: str = "modern",
        festival: str = None,
        price_range: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate textile poster using Gemini
        
        Args:
            fabric_type: Type of fabric (saree, kurta, etc.)
            offer_text: Text for the offer/promotion
            theme: Design theme
            festival: Festival name (optional)
            price_range: Price range (optional)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        # Create poster-specific prompt
        prompt_parts = [
            f"Create a beautiful, professional poster for {fabric_type}",
            f"Offer text: '{offer_text}'",
            f"Style: {theme}",
        ]
        
        if festival:
            prompt_parts.append(f"Festival theme: {festival}")
        
        if price_range:
            prompt_parts.append(f"Price range: {price_range}")
        
        prompt_parts.extend([
            "High quality, professional textile design",
            "Vibrant colors, intricate patterns",
            "Suitable for fashion and textile industry",
            "Clean, modern aesthetic",
            "Include the offer text prominently in the design",
            "Make it eye-catching and promotional"
        ])
        
        prompt = ", ".join(prompt_parts)
        
        return self.generate_image(
            prompt=prompt,
            aspect_ratio=kwargs.get('aspect_ratio', '1:1'),
            style=kwargs.get('style', 'photorealistic'),
            **kwargs
        )
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt based on style"""
        style_enhancements = {
            'photorealistic': "Photorealistic, high-resolution, professional photography style",
            'illustration': "Stylized illustration, artistic, creative design",
            'minimalist': "Minimalist design, clean lines, simple composition",
            'vintage': "Vintage style, retro aesthetic, classic design",
            'modern': "Modern design, contemporary style, sleek aesthetic"
        }
        
        enhancement = style_enhancements.get(style, "High quality, professional")
        return f"{enhancement}. {prompt}"
    
    def _process_response(self, response, prompt: str, processing_time: float) -> Dict[str, Any]:
        """Process Gemini API response"""
        try:
            image_urls = []
            image_data_list = []
            
            # Extract images from response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    logger.info(f"Text response: {part.text}")
                elif part.inline_data is not None:
                    # Save the image
                    image_url = self._save_image_data(part.inline_data.data, part.inline_data.mime_type)
                    if image_url:
                        image_urls.append(image_url)
                        image_data_list.append({
                            'data': part.inline_data.data,
                            'mime_type': part.inline_data.mime_type
                        })
            
            if image_urls:
                return {
                    "success": True,
                    "data": {
                        "prompt_used": prompt,
                        "generation_id": f"gemini_{int(time.time())}",
                        "model_used": self.model_name,
                        "processing_time": processing_time,
                        "image_urls": image_urls,
                        "image_data": image_data_list
                    },
                    "urls": image_urls,
                    "cost": self._calculate_cost(prompt)
                }
            else:
                return {
                    "success": False,
                    "error": "No images generated",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing response: {str(e)}",
                "data": None
            }
    
    def _save_image_data(self, image_data: bytes, mime_type: str) -> str:
        """Save image data and return URL"""
        try:
            # In a real implementation, you would save this to your storage service
            # For now, we'll create a unique filename and return a placeholder URL
            import uuid
            file_extension = mime_type.split('/')[-1] if '/' in mime_type else 'png'
            filename = f"gemini_{uuid.uuid4().hex[:8]}.{file_extension}"
            
            # You would typically save to AWS S3, Google Cloud Storage, etc.
            # For development, we'll use a placeholder
            return f"https://example.com/generated/{filename}"
            
        except Exception as e:
            logger.error(f"Error saving image data: {str(e)}")
            return None
    
    def _calculate_cost(self, prompt: str) -> float:
        """Calculate estimated cost for Gemini API usage"""
        # Gemini pricing (example rates - check current pricing)
        # Rough estimation based on prompt length
        input_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        output_tokens = 1000  # Estimated for image generation
        
        input_cost = (input_tokens / 1000) * 0.0005
        output_cost = (output_tokens / 1000) * 0.0015
        
        return round(input_cost + output_cost, 6)
    
    def _get_cache_key(self, prompt: str, aspect_ratio: str, style: str, num_images: int) -> str:
        """Generate cache key for request"""
        key_data = f"{prompt}_{aspect_ratio}_{style}_{num_images}"
        return f"gemini_image:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def generate_multiple_styles(
        self,
        prompt: str,
        styles: List[str] = None,
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """
        Generate images in multiple styles
        
        Args:
            prompt: Base prompt for image generation
            styles: List of styles to generate
            aspect_ratio: Aspect ratio for images
            
        Returns:
            Dict containing results for all styles
        """
        if styles is None:
            styles = ['photorealistic', 'illustration', 'minimalist']
        
        results = {}
        
        for style in styles:
            try:
                result = self.generate_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    style=style
                )
                results[style] = result
            except Exception as e:
                logger.error(f"Error generating {style} style: {str(e)}")
                results[style] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "success": True,
            "data": results,
            "total_styles": len(styles)
        }


# Global instance
gemini_image_generator = GeminiImageGenerator()
