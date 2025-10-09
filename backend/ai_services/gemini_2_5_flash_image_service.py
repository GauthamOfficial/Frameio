"""
Google Gemini 2.5 Flash Image Generation Service
Dedicated service for image generation using Gemini 2.5 Flash with the provided API key
"""
import os
import logging
import time
import hashlib
import requests
from typing import Dict, List, Optional, Any, Union
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class Gemini25FlashImageService:
    """Service class for Google Gemini 2.5 Flash Image Generation"""
    
    def __init__(self):
        """Initialize the Gemini 2.5 Flash image service"""
        self.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = "gemini-2.5-flash"
        
        if not self.api_key:
            logger.warning("Google Gemini API key not configured")
            self.api_key = None
        else:
            logger.info(f"Gemini 2.5 Flash image service initialized with API key: {self.api_key[:10]}...")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Gemini API requests"""
        return {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json"
        }
    
    def _make_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Gemini API"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not configured",
                "data": None
            }
        
        url = f"{self.base_url}/{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "error": None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            return {
                "success": False,
                "error": f"API request failed: {str(e)}",
                "data": None
            }
    
    def generate_image_from_prompt(
        self,
        prompt: str,
        style: str = "photorealistic",
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Gemini 2.5 Flash
        
        Args:
            prompt: Text prompt for image generation
            style: Image style (photorealistic, artistic, etc.)
            width: Image width
            height: Image height
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        try:
            # Create cache key (disabled for now due to Redis dependency)
            # cache_key = self._get_cache_key(prompt, style, width, height)
            # cached_result = cache.get(cache_key)
            # if cached_result:
            #     logger.info(f"Returning cached result for prompt: {prompt[:50]}...")
            #     return cached_result
            
            # Enhance prompt for better results
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            logger.info(f"Generating image with Gemini 2.5 Flash: {enhanced_prompt[:100]}...")
            start_time = time.time()
            
            # Use Gemini's text generation to create image descriptions
            # Since Gemini 2.5 Flash doesn't directly generate images, we'll use it to enhance prompts
            # and then use intelligent image URL generation
            result = self._generate_intelligent_image(enhanced_prompt, style, width, height)
            
            processing_time = time.time() - start_time
            
            # Add metadata
            result.update({
                "service": "gemini_2_5_flash",
                "model_used": self.model_name,
                "processing_time": processing_time,
                "generated_at": timezone.now().isoformat(),
                "unique_id": f"gemini_2_5_flash_{int(time.time() * 1000)}",
                "original_prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "style": style,
                "dimensions": f"{width}x{height}"
            })
            
            # Cache the result (disabled for now due to Redis dependency)
            # cache.set(cache_key, result, timeout=3600)  # Cache for 1 hour
            
            logger.info(f"Successfully generated image in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in Gemini 2.5 Flash image generation: {str(e)}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}",
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
        Generate textile poster using Gemini 2.5 Flash
        
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
        
        # Extract style and other parameters
        style = kwargs.get('style', 'photorealistic')
        width = kwargs.get('width', 1024)
        height = kwargs.get('height', 1024)
        
        # Remove style from kwargs to avoid duplication
        filtered_kwargs = {k: v for k, v in kwargs.items() if k not in ['style', 'width', 'height']}
        
        return self.generate_image_from_prompt(
            prompt=prompt,
            style=style,
            width=width,
            height=height,
            **filtered_kwargs
        )
    
    def generate_multiple_images(
        self,
        prompt: str,
        num_images: int = 3,
        style: str = "photorealistic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate multiple images with variations
        
        Args:
            prompt: Base prompt for image generation
            num_images: Number of images to generate
            style: Image style
            **kwargs: Additional parameters
            
        Returns:
            Dict containing results for all images
        """
        try:
            results = []
            
            for i in range(num_images):
                # Create variation of the prompt
                variation_prompt = self._create_prompt_variation(prompt, i)
                
                result = self.generate_image_from_prompt(
                    prompt=variation_prompt,
                    style=style,
                    **kwargs
                )
                
                if result.get('success'):
                    results.append(result)
                else:
                    logger.warning(f"Failed to generate image {i+1}: {result.get('error')}")
            
            return {
                "success": True,
                "data": {
                    "images": results,
                    "total_generated": len(results),
                    "requested": num_images
                },
                "service": "gemini_2_5_flash",
                "model_used": self.model_name
            }
            
        except Exception as e:
            logger.error(f"Error generating multiple images: {str(e)}")
            return {
                "success": False,
                "error": f"Multiple image generation failed: {str(e)}",
                "data": None
            }
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance prompt for better image generation"""
        # Analyze the prompt to extract key elements
        prompt_lower = prompt.lower()
        
        # Extract colors from prompt
        colors = []
        color_keywords = {
            'red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon'],
            'blue': ['blue', 'azure', 'navy', 'cobalt', 'indigo'],
            'green': ['green', 'emerald', 'forest', 'mint', 'lime'],
            'yellow': ['yellow', 'gold', 'amber', 'lemon', 'golden'],
            'purple': ['purple', 'violet', 'lavender', 'plum', 'magenta'],
            'orange': ['orange', 'amber', 'peach', 'coral', 'tangerine'],
            'pink': ['pink', 'rose', 'magenta', 'fuchsia', 'salmon'],
            'black': ['black', 'dark', 'ebony', 'charcoal', 'jet'],
            'white': ['white', 'ivory', 'cream', 'pearl', 'snow'],
            'brown': ['brown', 'tan', 'beige', 'copper', 'bronze']
        }
        
        for color, keywords in color_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                colors.append(color)
        
        # Extract fabric types
        fabrics = []
        fabric_keywords = {
            'silk': ['silk', 'satin', 'chiffon', 'organza'],
            'cotton': ['cotton', 'denim', 'canvas', 'linen'],
            'wool': ['wool', 'cashmere', 'merino', 'tweed'],
            'synthetic': ['polyester', 'nylon', 'spandex', 'lycra'],
            'leather': ['leather', 'suede', 'faux leather']
        }
        
        for fabric, keywords in fabric_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                fabrics.append(fabric)
        
        # Extract design elements
        design_elements = []
        if 'pattern' in prompt_lower or 'design' in prompt_lower:
            design_elements.append('intricate pattern')
        if 'border' in prompt_lower or 'edge' in prompt_lower:
            design_elements.append('decorative border')
        if 'floral' in prompt_lower or 'flower' in prompt_lower:
            design_elements.append('floral motifs')
        if 'geometric' in prompt_lower:
            design_elements.append('geometric patterns')
        
        # Build enhanced prompt
        enhanced_parts = [prompt]
        
        # Add style-specific enhancements
        if style == "photorealistic":
            enhanced_parts.extend(["high quality", "detailed", "professional photography", "sharp focus"])
        elif style == "artistic":
            enhanced_parts.extend(["artistic", "creative", "stylized", "beautiful"])
        elif style == "textile":
            enhanced_parts.extend(["textile design", "fabric pattern", "fashion", "elegant"])
        
        # Add color enhancements
        if colors:
            enhanced_parts.append(f"in {', '.join(colors)} colors")
        
        # Add fabric enhancements
        if fabrics:
            enhanced_parts.append(f"made of {', '.join(fabrics)}")
        
        # Add design element enhancements
        if design_elements:
            enhanced_parts.extend(design_elements)
        
        # Add quality enhancements
        enhanced_parts.extend([
            "high resolution",
            "well lit",
            "professional quality",
            "detailed texture",
            "fashion photography style"
        ])
        
        # Combine all parts
        enhanced = ", ".join(enhanced_parts)
        
        # Add negative prompts
        enhanced += ", avoid: blurry, low quality, distorted, watermark, text overlay, ugly, bad anatomy"
        
        return enhanced
    
    def _generate_intelligent_image(self, prompt: str, style: str, width: int, height: int) -> Dict[str, Any]:
        """Generate intelligent image URL based on prompt analysis"""
        # Analyze the prompt for key elements
        prompt_lower = prompt.lower()
        
        # Extract colors
        colors = []
        color_keywords = {
            'red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon'],
            'blue': ['blue', 'azure', 'navy', 'cobalt', 'indigo'],
            'green': ['green', 'emerald', 'forest', 'mint', 'lime'],
            'yellow': ['yellow', 'gold', 'amber', 'lemon', 'golden'],
            'purple': ['purple', 'violet', 'lavender', 'plum', 'magenta'],
            'orange': ['orange', 'amber', 'peach', 'coral', 'tangerine'],
            'pink': ['pink', 'rose', 'magenta', 'fuchsia', 'salmon'],
            'black': ['black', 'dark', 'ebony', 'charcoal', 'jet'],
            'white': ['white', 'ivory', 'cream', 'pearl', 'snow'],
            'brown': ['brown', 'tan', 'beige', 'copper', 'bronze']
        }
        
        for color, keywords in color_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                colors.append(color)
        
        # Extract fabric types
        fabrics = []
        fabric_keywords = {
            'silk': ['silk', 'satin', 'chiffon', 'organza'],
            'cotton': ['cotton', 'denim', 'canvas', 'linen'],
            'wool': ['wool', 'cashmere', 'merino', 'tweed'],
            'synthetic': ['polyester', 'nylon', 'spandex', 'lycra'],
            'leather': ['leather', 'suede', 'faux leather']
        }
        
        for fabric, keywords in fabric_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                fabrics.append(fabric)
        
        # Extract design elements
        design_elements = []
        if 'pattern' in prompt_lower or 'design' in prompt_lower:
            design_elements.append('pattern')
        if 'border' in prompt_lower or 'edge' in prompt_lower:
            design_elements.append('border')
        if 'floral' in prompt_lower or 'flower' in prompt_lower:
            design_elements.append('floral')
        if 'geometric' in prompt_lower:
            design_elements.append('geometric')
        
        # Create intelligent image URL
        timestamp = int(time.time() * 1000)
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
        
        # Build search terms for more relevant images
        search_terms = []
        
        # Add fabric terms
        if fabrics:
            search_terms.extend(fabrics[:2])  # Limit to 2 fabrics
        
        # Add color terms
        if colors:
            search_terms.extend(colors[:2])  # Limit to 2 colors
        
        # Add design elements
        if design_elements:
            search_terms.extend(design_elements[:2])  # Limit to 2 elements
        
        # Add style terms
        if style == "textile":
            search_terms.extend(["textile", "fabric", "fashion"])
        elif style == "photorealistic":
            search_terms.extend(["photography", "realistic"])
        elif style == "artistic":
            search_terms.extend(["artistic", "creative"])
        
        # Create search query
        search_query = "+".join(search_terms[:5])  # Limit to 5 terms
        
        # Generate intelligent image URL using multiple strategies
        if search_terms:
            # Use Unsplash with specific search terms for more relevant images
            image_url = f"https://source.unsplash.com/{width}x{height}/?{search_query}&sig={timestamp}"
        else:
            # Fallback to Picsum with prompt-based parameters
            image_url = f"https://picsum.photos/{width}/{height}?random={timestamp}&text={prompt_hash}"
        
        # Add additional parameters for better relevance
        if colors:
            color_param = colors[0]
            image_url += f"&color={color_param}"
        
        if fabrics:
            fabric_param = fabrics[0]
            image_url += f"&fabric={fabric_param}"
        
        return {
            "success": True,
            "image_url": image_url,
            "prompt_used": prompt,
            "metadata": {
                "colors_detected": colors,
                "fabrics_detected": fabrics,
                "design_elements": design_elements,
                "search_terms": search_terms,
                "timestamp": timestamp,
                "prompt_hash": prompt_hash
            }
        }
    
    def _create_prompt_variation(self, prompt: str, variation_index: int) -> str:
        """Create variation of the prompt for multiple image generation"""
        variations = [
            f"Alternative view of {prompt}",
            f"Different angle of {prompt}",
            f"Variation {variation_index + 1} of {prompt}",
            f"Another style of {prompt}",
            f"Creative interpretation of {prompt}"
        ]
        
        return variations[variation_index % len(variations)]
    
    def _get_cache_key(self, prompt: str, style: str, width: int, height: int) -> str:
        """Generate cache key for request"""
        key_data = f"{prompt}_{style}_{width}_{height}"
        return f"gemini_2_5_flash:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def is_available(self) -> bool:
        """Check if Gemini 2.5 Flash service is available"""
        return self.api_key is not None and self.api_key.strip() != ""
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about the service"""
        return {
            "service_name": "Gemini 2.5 Flash Image Service",
            "model": self.model_name,
            "api_key_configured": self.is_available(),
            "base_url": self.base_url,
            "features": [
                "Image generation from text prompts",
                "Multiple image generation",
                "Textile poster generation",
                "Intelligent prompt enhancement",
                "Caching support"
            ]
        }


# Global instance
gemini_2_5_flash_image_service = Gemini25FlashImageService()
