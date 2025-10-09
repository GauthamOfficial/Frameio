"""
NanoBanana AI Service for textile poster and caption generation
Using the official NanoBanana Python SDK
"""
import os
import logging
import time
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class NanoBananaError(Exception):
    """Custom exception for NanoBanana API errors"""
    pass


class NanoBananaAIService:
    """Service class for NanoBanana AI integration using official SDK"""
    
    def __init__(self):
        """Initialize the NanoBanana client"""
        self.api_key = settings.NANOBANANA_API_KEY
        self.base_url = "https://api.nanobanana.ai"
        
        # Always initialize with fallback capability
        self.client = None
        self.use_fallback = True  # Default to fallback mode
        
        if not self.api_key or self.api_key == '':
            logger.info("NANOBANANA_API_KEY not configured - using fallback mode")
            self.use_fallback = True
        else:
            try:
                import requests
                self.client = requests.Session()
                self.client.headers.update({
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                })
                logger.info("NanoBanana REST API client initialized successfully")
                self.use_fallback = False
            except Exception as e:
                logger.warning(f"Failed to initialize NanoBanana client: {str(e)} - using fallback mode")
                self.client = None
                self.use_fallback = True
    
    def generate_poster(self, image_url: str, offer_text: str, theme: str) -> Dict[str, Any]:
        """
        Generate a textile poster using NanoBanana AI
        
        Args:
            image_url: URL of the fabric image
            offer_text: Text for the offer/promotion
            theme: Design theme (modern, traditional, festive, etc.)
            
        Returns:
            Dict containing generated poster data
        """
        try:
            # Check cache first (disabled for development to ensure fresh content)
            # cache_key = f"ai_poster_{hash(f'{image_url}_{offer_text}_{theme}')}"
            # cached_result = self.get_cached_result(cache_key)
            # if cached_result:
            #     logger.info(f"Returning cached poster result for key: {cache_key}")
            #     return cached_result
            
            if not self.client or self.use_fallback:
                logger.info("Using fallback mode for image generation")
                return self._try_alternative_service(image_url, offer_text, theme)
            
            # Create structured prompt for textile poster
            prompt = self._create_poster_prompt(image_url, offer_text, theme)
            
            # Generate image using NanoBanana REST API
            logger.info(f"Generating poster with NanoBanana for theme: {theme}")
            
            # Use the correct NanoBanana API endpoint for image generation
            # Since NanoBanana is primarily for image editing, we'll use a text-to-image approach
            payload = {
                "prompt": prompt,
                "style": "cinematic",
                "aspect_ratio": "1:1",
                "quality": "high"
            }
            
            # Try the style-transfer endpoint as it's closest to generation
            try:
                logger.info(f"Attempting NanoBanana API call to {self.base_url}/v1/images/style-transfer")
                response = self.client.post(f"{self.base_url}/v1/images/style-transfer", json=payload, timeout=60)
                
                logger.info(f"API response status: {response.status_code}")
                logger.info(f"API response text: {response.text[:200]}...")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Process the result
                    if result and 'images' in result:
                        image_urls = result['images']
                        
                        if not image_urls:
                            raise NanoBananaError("No image URLs returned from NanoBanana")
                        
                        # Cache the result for 24 hours
                        try:
                            from django.core.cache import cache
                            cache_data = {
                                'image_urls': image_urls,
                                'prompt': prompt,
                                'generated_at': timezone.now().isoformat(),
                                'theme': theme,
                                'offer_text': offer_text
                            }
                            cache.set(cache_key, cache_data, timeout=86400)  # 24 hours
                        except Exception as cache_error:
                            logger.warning(f"Failed to cache result: {str(cache_error)} - continuing without cache")
                        
                        logger.info(f"Successfully generated {len(image_urls)} images from NanoBanana API")
                        return {
                            'success': True,
                            'image_urls': image_urls,
                            'prompt_used': prompt,
                            'theme': theme,
                            'offer_text': offer_text,
                            'generation_id': result.get('id', f"nano_{int(time.time())}"),
                            'cost': self._calculate_cost(),
                            'cached': False
                        }
                    else:
                        raise NanoBananaError("No images in response from NanoBanana API")
                else:
                    raise NanoBananaError(f"NanoBanana API error: {response.status_code} - {response.text}")
            except Exception as api_error:
                logger.warning(f"NanoBanana API call failed: {str(api_error)}, using fallback")
                raise NanoBananaError(f"API call failed: {str(api_error)}")
                
        except NanoBananaError as e:
            logger.error(f"NanoBanana API error: {str(e)}")
            # Try alternative image service
            return self._try_alternative_service(image_url, offer_text, theme)
        except Exception as e:
            logger.error(f"Unexpected error in poster generation: {str(e)}")
            # Try alternative image service
            return self._try_alternative_service(image_url, offer_text, theme)
    
    def generate_caption(self, product_name: str, description: str) -> Dict[str, Any]:
        """
        Generate AI caption for textile product
        
        Args:
            product_name: Name of the product
            description: Product description
            
        Returns:
            Dict containing generated captions
        """
        try:
            # Check cache first (disabled for development to ensure fresh content)
            # cache_key = f"ai_caption_{hash(f'{product_name}_{description}')}"
            # cached_result = self.get_cached_result(cache_key)
            # if cached_result:
            #     logger.info(f"Returning cached caption result for key: {cache_key}")
            #     return cached_result
            
            if not self.client:
                logger.warning("NanoBanana client not available, using fallback")
                return self._get_fallback_caption_result(product_name, description)
            
            # Create structured prompt for caption generation
            prompt = self._create_caption_prompt(product_name, description)
            
            # Generate caption using NanoBanana REST API
            logger.info(f"Generating caption with NanoBanana for product: {product_name}")
            
            # NanoBanana doesn't have text generation, so we'll use a fallback approach
            # For now, we'll return the fallback result since NanoBanana is image-focused
            logger.info("NanoBanana API is image-focused, using fallback for caption generation")
            return self._get_fallback_caption_result(product_name, description)
                
        except NanoBananaError as e:
            logger.error(f"NanoBanana API error: {str(e)}")
            return self._get_fallback_caption_result(product_name, description)
        except Exception as e:
            logger.error(f"Unexpected error in caption generation: {str(e)}")
            return self._get_fallback_caption_result(product_name, description)
    
    def _create_poster_prompt(self, image_url: str, offer_text: str, theme: str) -> str:
        """Create structured prompt for poster generation"""
        theme_enhancements = {
            'modern': 'modern design, clean lines, minimalist aesthetic, contemporary style',
            'traditional': 'traditional patterns, classic motifs, cultural elements, heritage design',
            'festive': 'festive colors, celebration theme, joyful atmosphere, special occasion',
            'elegant': 'elegant design, sophisticated style, luxury feel, refined aesthetics',
            'casual': 'casual style, comfortable design, everyday wear, relaxed atmosphere'
        }
        
        theme_desc = theme_enhancements.get(theme.lower(), 'beautiful design')
        
        prompt = f"""Generate a textile poster for {offer_text}, using a {theme} fabric theme with soft lighting.
        
        Design requirements:
        - High-quality textile poster design
        - Professional commercial use
        - {theme_desc}
        - Include offer text: "{offer_text}"
        - Soft, natural lighting
        - Textile fabric focus
        - Modern composition
        - Clean, readable text overlay
        - Professional photography style
        
        Style: cinematic, high resolution, commercial quality"""
        
        return prompt
    
    def _create_caption_prompt(self, product_name: str, description: str) -> str:
        """Create structured prompt for caption generation"""
        prompt = f"""Generate 5 engaging social media captions for a textile product.
        
        Product: {product_name}
        Description: {description}
        
        Requirements:
        - 5 different caption variations
        - Include relevant hashtags
        - Different tones: professional, casual, festive, elegant, marketing
        - 1-2 sentences each
        - Include emojis appropriately
        - Focus on textile/fabric appeal
        - Include price appeal if mentioned
        
        Format each caption on a new line starting with "Caption X:" where X is the number."""
        
        return prompt
    
    def _parse_captions(self, text: str) -> List[Dict[str, Any]]:
        """Parse generated captions from text response"""
        captions = []
        lines = text.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('Caption'):
                # Clean up the caption text
                caption_text = line.strip()
                if caption_text:
                    captions.append({
                        'text': caption_text,
                        'tone': self._determine_tone(caption_text),
                        'effectiveness_score': self._calculate_effectiveness_score(caption_text),
                        'hashtags': self._extract_hashtags(caption_text)
                    })
        
        # If no structured captions found, create from the text
        if not captions and text.strip():
            captions.append({
                'text': text.strip(),
                'tone': 'general',
                'effectiveness_score': 7.0,
                'hashtags': self._extract_hashtags(text)
            })
        
        return captions[:5]  # Limit to 5 captions
    
    def _determine_tone(self, text: str) -> str:
        """Determine the tone of a caption"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['sale', 'offer', 'discount', 'deal']):
            return 'marketing'
        elif any(word in text_lower for word in ['elegant', 'luxury', 'premium', 'sophisticated']):
            return 'elegant'
        elif any(word in text_lower for word in ['festive', 'celebration', 'party', 'special']):
            return 'festive'
        elif any(word in text_lower for word in ['comfortable', 'casual', 'everyday', 'relaxed']):
            return 'casual'
        else:
            return 'professional'
    
    def _calculate_effectiveness_score(self, text: str) -> float:
        """Calculate effectiveness score for a caption"""
        score = 5.0  # Base score
        
        # Length bonus (optimal 50-150 characters)
        length = len(text)
        if 50 <= length <= 150:
            score += 2.0
        elif 30 <= length <= 200:
            score += 1.0
        
        # Hashtag bonus
        hashtag_count = text.count('#')
        if 2 <= hashtag_count <= 5:
            score += 1.5
        elif hashtag_count > 0:
            score += 0.5
        
        # Emoji bonus
        emoji_count = sum(1 for char in text if ord(char) > 127)
        if 1 <= emoji_count <= 3:
            score += 1.0
        
        # Action words bonus
        action_words = ['buy', 'shop', 'get', 'grab', 'discover', 'explore', 'find']
        if any(word in text.lower() for word in action_words):
            score += 1.0
        
        return min(10.0, max(1.0, score))
    
    def _extract_hashtags(self, text: str) -> List[str]:
        """Extract hashtags from text"""
        import re
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    
    def _calculate_cost(self) -> float:
        """Calculate estimated cost for NanoBanana API usage"""
        # Base cost estimation
        return 0.05
    
    def _get_fallback_poster_result(self, image_url: str, offer_text: str, theme: str) -> Dict[str, Any]:
        """Get fallback result when API is unavailable"""
        # Create textile-specific fallback images based on theme
        fallback_images = self._generate_fallback_images(theme, offer_text)
        
        return {
            'success': True,
            'image_urls': fallback_images,
            'prompt_used': f"Fallback poster for {offer_text} with {theme} theme",
            'theme': theme,
            'offer_text': offer_text,
            'generation_id': f"fallback_{int(time.time())}",
            'cost': 0.0,
            'cached': False,
            'fallback': True
        }
    
    def _generate_fallback_images(self, theme: str, offer_text: str) -> List[str]:
        """Generate fallback images based on theme"""
        import time
        import hashlib
        
        # Create unique fallback images using timestamp and content hash
        timestamp = int(time.time() * 1000)  # Use milliseconds for better uniqueness
        content_hash = hashlib.md5(f"{theme}{offer_text}{timestamp}".encode()).hexdigest()[:8]
        
        fallback_images = []
        
        # Theme-based color schemes
        color_schemes = {
            'modern': ['FF6B6B', '4ECDC4', '45B7D1', '96CEB4'],
            'traditional': ['D4AF37', 'B8860B', 'CD853F', 'DEB887'],
            'festive': ['FFD700', 'FF6347', 'FF1493', 'FF4500'],
            'elegant': ['2C3E50', '34495E', '7F8C8D', '95A5A6']
        }
        
        colors = color_schemes.get(theme.lower(), color_schemes['modern'])
        
        # Generate reliable fallback images using multiple sources
        for i, color in enumerate(colors[:3]):  # Generate 3 images
            # Create unique identifiers for each image
            unique_id = f"{timestamp}_{content_hash}_{i}"
            
            # Create reliable placeholder images
            if i == 0:
                # Use placeholder.com with theme-specific styling
                text = f"{theme.title()}+{offer_text.replace(' ', '+')}"
                image_url = f"https://via.placeholder.com/1024x1024/{color}/FFFFFF?text={text}&timestamp={timestamp}"
            elif i == 1:
                # Use Picsum with unique seed for variety
                seed = hash(f"{theme}{offer_text}{timestamp}") % 10000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024"
            else:
                # Use Lorem Picsum with different parameters
                random_id = (hash(f"{theme}{offer_text}{timestamp}") % 1000) + 1
                image_url = f"https://picsum.photos/id/{random_id}/1024/1024"
            
            fallback_images.append(image_url)
        
        # Add reliable textile-specific stock images
        textile_fallbacks = [
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=1024&h=1024&fit=crop&crop=center",  # Fabric texture
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1024&h=1024&fit=crop&crop=center",  # Textile design
            "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1024&h=1024&fit=crop&crop=center",  # Fashion textile
            "https://images.unsplash.com/photo-1594633312681-425c7b97ccd1?w=1024&h=1024&fit=crop&crop=center",  # Textile pattern
            "https://images.unsplash.com/photo-1558769132-cb1aea458c5e?w=1024&h=1024&fit=crop&crop=center",  # Fabric close-up
        ]
        
        # Combine generated and stock images
        all_images = fallback_images + textile_fallbacks[:2]  # Add 2 stock images
        
        logger.info(f"Generated {len(all_images)} fallback images for theme: {theme}")
        return all_images
    
    def _get_fallback_caption_result(self, product_name: str, description: str) -> Dict[str, Any]:
        """Get fallback result for captions when API is unavailable"""
        # Generate unique captions with timestamp
        import time
        timestamp = int(time.time() * 1000)
        
        fallback_captions = [
            {
                'text': f"✨ {product_name} - {description} ✨ #Textile #Fashion #{timestamp % 1000}",
                'tone': 'professional',
                'effectiveness_score': 7.5,
                'hashtags': ['#Textile', '#Fashion', f'#{timestamp % 1000}']
            },
            {
                'text': f"Discover the beauty of {product_name} 🎨 #Style #Quality #{timestamp % 1000}",
                'tone': 'casual',
                'effectiveness_score': 7.0,
                'hashtags': ['#Style', '#Quality', f'#{timestamp % 1000}']
            },
            {
                'text': f"Elegant {product_name} for special occasions 💫 #Elegance #Luxury #{timestamp % 1000}",
                'tone': 'elegant',
                'effectiveness_score': 8.0,
                'hashtags': ['#Elegance', '#Luxury', f'#{timestamp % 1000}']
            }
        ]
        
        return {
            'success': True,
            'captions': fallback_captions,
            'prompt_used': f"Fallback captions for {product_name}",
            'product_name': product_name,
            'generation_id': f"fallback_caption_{int(time.time())}",
            'cost': 0.0,
            'cached': False,
            'fallback': True
        }
    
    def get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result if available"""
        try:
            from django.core.cache import cache
            result = cache.get(cache_key)
            if result:
                result['cached'] = True
                return result
        except Exception as e:
            logger.warning(f"Cache not available: {str(e)} - continuing without cache")
        return None
    
    def _try_alternative_service(self, image_url: str, offer_text: str, theme: str) -> Dict[str, Any]:
        """Try alternative image service when NanoBanana fails"""
        try:
            # Try dynamic image service first
            from .dynamic_image_service import DynamicImageService
            dynamic_service = DynamicImageService()
            result = dynamic_service.generate_poster(image_url, offer_text, theme)
            
            if result.get('success'):
                logger.info("Dynamic image service generated images successfully")
                return result
            else:
                logger.warning("Dynamic image service failed, trying alternative service")
                # Fallback to alternative service
                from .alternative_image_service import AlternativeImageService
                alt_service = AlternativeImageService()
                result = alt_service.generate_poster(image_url, offer_text, theme)
                
                if result.get('success'):
                    logger.info("Alternative image service generated images successfully")
                    return result
                else:
                    logger.warning("Alternative image service also failed, using fallback")
                    return self._get_fallback_poster_result(image_url, offer_text, theme)
                
        except Exception as e:
            logger.error(f"Alternative service failed: {str(e)}")
            return self._get_fallback_poster_result(image_url, offer_text, theme)
    
    def is_available(self) -> bool:
        """Check if NanoBanana service is available"""
        return self.client is not None and self.api_key is not None
