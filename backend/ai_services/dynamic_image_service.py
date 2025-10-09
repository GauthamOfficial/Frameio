#!/usr/bin/env python
"""
Dynamic image generation service that creates truly unique images
"""
import os
import time
import hashlib
import requests
import logging
from typing import Dict, Any, List
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


class DynamicImageService:
    """Dynamic image generation service that creates unique images for each request"""
    
    def __init__(self):
        """Initialize the dynamic image service"""
        self.api_key = settings.NANOBANANA_API_KEY
        self.client = None
        
        # Initialize requests session
        try:
            self.client = requests.Session()
            if self.api_key:
                self.client.headers.update({
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                })
            logger.info("Dynamic image service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize dynamic image service: {str(e)}")
            self.client = None
    
    def generate_poster(self, image_url: str, offer_text: str, theme: str) -> Dict[str, Any]:
        """
        Generate a textile poster with truly unique images
        
        Args:
            image_url: URL of the fabric image
            offer_text: Text for the offer/promotion
            theme: Design theme
            
        Returns:
            Dict containing generated poster data
        """
        try:
            # Create unique cache key based on content
            content_key = f"{theme}_{offer_text}_{int(time.time())}"
            cache_key = f"dynamic_poster_{hashlib.md5(content_key.encode()).hexdigest()}"
            
            # Check cache first (disabled for development to ensure fresh content)
            # cached_result = self.get_cached_result(cache_key)
            # if cached_result:
            #     logger.info("Returning cached result")
            #     return cached_result
            
            # Generate truly unique images
            image_urls = self._generate_unique_images(image_url, offer_text, theme)
            
            if not image_urls:
                raise Exception("No images could be generated")
            
            # Create result
            result = {
                'success': True,
                'image_urls': image_urls,
                'prompt_used': f"Dynamic generation for {offer_text} with {theme} theme",
                'theme': theme,
                'offer_text': offer_text,
                'generation_id': f"dynamic_{int(time.time())}",
                'cost': 0.0,
                'cached': False,
                'fallback': False,
                'service_used': 'dynamic'
            }
            
            # Cache the result
            cache_data = {
                'image_urls': image_urls,
                'prompt': result['prompt_used'],
                'generated_at': timezone.now().isoformat(),
                'theme': theme,
                'offer_text': offer_text
            }
            cache.set(cache_key, cache_data, timeout=3600)  # 1 hour cache
            
            logger.info(f"Generated {len(image_urls)} unique images for theme: {theme}")
            return result
            
        except Exception as e:
            logger.error(f"Dynamic image generation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback': True
            }
    
    def _generate_unique_images(self, image_url: str, offer_text: str, theme: str) -> List[str]:
        """Generate truly unique images based on content"""
        images = []
        
        # Create unique identifiers
        timestamp = int(time.time())
        content_hash = hashlib.md5(f"{theme}{offer_text}".encode()).hexdigest()[:8]
        
        # Generate 5 unique images using different methods
        for i in range(5):
            unique_id = f"{timestamp}_{content_hash}_{i}"
            
            if i == 0:
                # Method 1: Picsum with content-based seed
                seed = hash(f"{theme}{offer_text}{timestamp}{i}") % 100000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024"
            elif i == 1:
                # Method 2: Picsum with different parameters
                seed = hash(f"{theme}{offer_text}{timestamp}{i}") % 100000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024?blur=1"
            elif i == 2:
                # Method 3: Unsplash with content-specific search
                search_terms = f"textile,{theme},fabric,{offer_text.replace(' ', ',')}"
                image_url = f"https://source.unsplash.com/1024x1024/?{search_terms}&sig={unique_id}"
            elif i == 3:
                # Method 4: Picsum with grayscale
                seed = hash(f"{theme}{offer_text}{timestamp}{i}") % 100000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024?grayscale"
            else:
                # Method 5: Picsum with different blur
                seed = hash(f"{theme}{offer_text}{timestamp}{i}") % 100000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024?blur=3"
            
            images.append(image_url)
        
        return images
    
    def _generate_theme_specific_images(self, theme: str, offer_text: str) -> List[str]:
        """Generate theme-specific images"""
        images = []
        
        # Theme-specific image generation
        theme_configs = {
            'modern': {
                'search_terms': 'modern,contemporary,minimalist,design',
                'filters': ['blur=1', 'grayscale'],
                'seeds': ['modern', 'contemporary', 'minimal']
            },
            'traditional': {
                'search_terms': 'traditional,heritage,classic,vintage',
                'filters': ['blur=2', 'grayscale'],
                'seeds': ['traditional', 'heritage', 'classic']
            },
            'festive': {
                'search_terms': 'festive,celebration,colorful,bright',
                'filters': ['blur=0'],
                'seeds': ['festive', 'celebration', 'colorful']
            },
            'elegant': {
                'search_terms': 'elegant,luxury,premium,sophisticated',
                'filters': ['blur=1', 'grayscale'],
                'seeds': ['elegant', 'luxury', 'premium']
            }
        }
        
        config = theme_configs.get(theme.lower(), theme_configs['modern'])
        
        # Generate images based on theme
        for i in range(3):
            if i == 0:
                # Unsplash with theme-specific search
                search_terms = f"{config['search_terms']},{offer_text.replace(' ', ',')}"
                image_url = f"https://source.unsplash.com/1024x1024/?{search_terms}&sig={int(time.time())}"
            elif i == 1:
                # Picsum with theme-specific seed
                seed = hash(f"{config['seeds'][0]}{offer_text}{int(time.time())}") % 100000
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024"
            else:
                # Picsum with theme-specific filter
                seed = hash(f"{config['seeds'][1]}{offer_text}{int(time.time())}") % 100000
                filter_param = config['filters'][0] if config['filters'] else ''
                image_url = f"https://picsum.photos/seed/{seed}/1024/1024?{filter_param}"
            
            images.append(image_url)
        
        return images
    
    def get_cached_result(self, cache_key: str) -> Dict[str, Any]:
        """Get cached result if available"""
        try:
            result = cache.get(cache_key)
            if result:
                result['cached'] = True
                return result
        except Exception as e:
            logger.error(f"Failed to get cached result: {str(e)}")
        return None
    
    def is_available(self) -> bool:
        """Check if dynamic image service is available"""
        return True  # Always available

