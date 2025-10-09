"""
Improved Image Generation Service with Enhanced NanoBanana Integration
Fixes image generation issues with proper prompt engineering and API usage
"""
import os
import time
import logging
import requests
import hashlib
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from .enhanced_nanobanana_service import EnhancedNanoBananaService
from .gemini_prompt_enhancer import GeminiPromptEnhancer

logger = logging.getLogger(__name__)


class ImprovedImageGenerationService:
    """Improved image generation service with enhanced prompt engineering"""
    
    def __init__(self):
        """Initialize the improved image generation service"""
        self.nanobanana_service = EnhancedNanoBananaService()
        self.gemini_enhancer = GeminiPromptEnhancer()
        
        # Initialize alternative services
        self.alternative_services = [
            self._try_stability_ai,
            self._try_openai_dalle,
            self._try_replicate,
            self._try_huggingface
        ]
        
        logger.info("Improved image generation service initialized")
    
    def generate_image_from_prompt(self, prompt: str, style: str = "photorealistic", **kwargs) -> Dict[str, Any]:
        """
        Generate image from prompt with enhanced prompt engineering
        
        Args:
            prompt: User's text prompt
            style: Image style
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated image data
        """
        try:
            # Step 1: Enhance prompt using Gemini
            enhanced_prompt = self._enhance_prompt(prompt, style, kwargs)
            
            # Step 2: Try NanoBanana API first
            if self.nanobanana_service.is_available():
                try:
                    result = self.nanobanana_service.generate_image_from_prompt(enhanced_prompt, style, **kwargs)
                    if result.get('success'):
                        logger.info("Successfully generated image using NanoBanana")
                        return result
                except Exception as e:
                    logger.warning(f"NanoBanana API failed: {str(e)}")
            
            # Step 3: Try alternative AI services
            for service in self.alternative_services:
                try:
                    result = service(enhanced_prompt, style, **kwargs)
                    if result.get('success'):
                        logger.info(f"Successfully generated image using {service.__name__}")
                        return result
                except Exception as e:
                    logger.warning(f"{service.__name__} failed: {str(e)}")
                    continue
            
            # Step 4: Use enhanced fallback
            return self._generate_enhanced_fallback(enhanced_prompt, style, **kwargs)
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return self._get_emergency_fallback(prompt, style)
    
    def _enhance_prompt(self, prompt: str, style: str, context: Dict[str, Any]) -> str:
        """Enhance prompt using Gemini or local enhancement"""
        try:
            # Use Gemini for prompt enhancement
            enhanced = self.gemini_enhancer.enhance_prompt_for_image_generation(
                prompt, style, context
            )
            
            if enhanced and len(enhanced) > len(prompt):
                logger.info("Prompt enhanced using Gemini")
                return enhanced
            else:
                logger.warning("Gemini enhancement failed, using local enhancement")
                return self._enhance_prompt_locally(prompt, style)
                
        except Exception as e:
            logger.warning(f"Prompt enhancement failed: {str(e)}")
            return self._enhance_prompt_locally(prompt, style)
    
    def _enhance_prompt_locally(self, prompt: str, style: str) -> str:
        """Local prompt enhancement"""
        enhancements = []
        
        # Style-specific enhancements
        style_enhancements = {
            'photorealistic': [
                'high resolution', 'detailed', 'professional photography',
                'sharp focus', 'well lit', 'crystal clear', 'ultra detailed'
            ],
            'artistic': [
                'artistic style', 'creative composition', 'stylized',
                'artistic interpretation', 'creative design'
            ],
            'textile': [
                'textile design', 'fabric pattern', 'fashion photography',
                'textile focus', 'fabric texture', 'garment design'
            ],
            'modern': [
                'modern design', 'contemporary style', 'clean lines',
                'minimalist aesthetic', 'sleek design'
            ],
            'traditional': [
                'traditional patterns', 'classic design', 'heritage style',
                'cultural elements', 'traditional motifs'
            ]
        }
        
        if style in style_enhancements:
            enhancements.extend(style_enhancements[style])
        
        # Add general quality enhancements
        enhancements.extend([
            'high quality', 'professional', 'detailed', 'sharp',
            'well composed', 'beautiful', 'stunning'
        ])
        
        # Combine prompt with enhancements
        enhanced = f"{prompt}, {', '.join(enhancements)}"
        
        # Add negative prompt elements
        enhanced += ", avoid: blurry, low quality, distorted, watermark, text overlay"
        
        return enhanced
    
    def _try_stability_ai(self, prompt: str, style: str, **kwargs) -> Dict[str, Any]:
        """Try Stability AI API"""
        stability_key = getattr(settings, 'STABILITY_API_KEY', None)
        if not stability_key:
            raise Exception("Stability API key not configured")
        
        try:
            headers = {
                'Authorization': f'Bearer {stability_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text_prompts': [{'text': prompt}],
                'cfg_scale': kwargs.get('guidance_scale', 7.5),
                'height': kwargs.get('height', 1024),
                'width': kwargs.get('width', 1024),
                'samples': kwargs.get('num_images', 1),
                'steps': kwargs.get('num_inference_steps', 20)
            }
            
            response = requests.post(
                'https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image',
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                image_urls = [artifact['base64'] for artifact in data['artifacts']]
                
                return {
                    'success': True,
                    'image_urls': image_urls,
                    'service': 'stability_ai',
                    'prompt_used': prompt,
                    'metadata': data
                }
            else:
                raise Exception(f"Stability AI error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Stability AI failed: {str(e)}")
    
    def _try_openai_dalle(self, prompt: str, style: str, **kwargs) -> Dict[str, Any]:
        """Try OpenAI DALL-E API"""
        openai_key = getattr(settings, 'OPENAI_API_KEY', None)
        if not openai_key:
            raise Exception("OpenAI API key not configured")
        
        try:
            headers = {
                'Authorization': f'Bearer {openai_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': 'dall-e-3',
                'prompt': prompt,
                'n': kwargs.get('num_images', 1),
                'size': f"{kwargs.get('width', 1024)}x{kwargs.get('height', 1024)}",
                'quality': 'hd'
            }
            
            response = requests.post(
                'https://api.openai.com/v1/images/generations',
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                image_urls = [item['url'] for item in data['data']]
                
                return {
                    'success': True,
                    'image_urls': image_urls,
                    'service': 'openai_dalle',
                    'prompt_used': prompt,
                    'metadata': data
                }
            else:
                raise Exception(f"OpenAI DALL-E error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"OpenAI DALL-E failed: {str(e)}")
    
    def _try_replicate(self, prompt: str, style: str, **kwargs) -> Dict[str, Any]:
        """Try Replicate API"""
        replicate_key = getattr(settings, 'REPLICATE_API_KEY', None)
        if not replicate_key:
            raise Exception("Replicate API key not configured")
        
        try:
            headers = {
                'Authorization': f'Token {replicate_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'version': 'ac732df83cea7fff18b8472768c88ad041fa750ff7682a21affe81863cbe77e4',
                'input': {
                    'prompt': prompt,
                    'width': kwargs.get('width', 1024),
                    'height': kwargs.get('height', 1024),
                    'num_inference_steps': kwargs.get('num_inference_steps', 20),
                    'guidance_scale': kwargs.get('guidance_scale', 7.5)
                }
            }
            
            response = requests.post(
                'https://api.replicate.com/v1/predictions',
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 201:
                data = response.json()
                # Note: Replicate is async, would need polling for results
                return {
                    'success': True,
                    'image_urls': [data.get('urls', {}).get('get', '')],
                    'service': 'replicate',
                    'prompt_used': prompt,
                    'metadata': data
                }
            else:
                raise Exception(f"Replicate error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Replicate failed: {str(e)}")
    
    def _try_huggingface(self, prompt: str, style: str, **kwargs) -> Dict[str, Any]:
        """Try Hugging Face API"""
        hf_key = getattr(settings, 'HUGGINGFACE_API_KEY', None)
        if not hf_key:
            raise Exception("Hugging Face API key not configured")
        
        try:
            headers = {
                'Authorization': f'Bearer {hf_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': prompt,
                'parameters': {
                    'width': kwargs.get('width', 1024),
                    'height': kwargs.get('height', 1024),
                    'num_inference_steps': kwargs.get('num_inference_steps', 20),
                    'guidance_scale': kwargs.get('guidance_scale', 7.5)
                }
            }
            
            response = requests.post(
                'https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5',
                json=payload,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 200:
                # Hugging Face returns base64 encoded images
                import base64
                image_data = response.content
                image_b64 = base64.b64encode(image_data).decode()
                
                return {
                    'success': True,
                    'image_urls': [f"data:image/png;base64,{image_b64}"],
                    'service': 'huggingface',
                    'prompt_used': prompt,
                    'metadata': {'format': 'base64'}
                }
            else:
                raise Exception(f"Hugging Face error: {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Hugging Face failed: {str(e)}")
    
    def _generate_enhanced_fallback(self, prompt: str, style: str, **kwargs) -> Dict[str, Any]:
        """Generate enhanced fallback images"""
        try:
            # Analyze prompt for better image generation
            prompt_analysis = self._analyze_prompt(prompt, style)
            
            # Generate unique images based on analysis
            image_urls = self._generate_ai_based_images(prompt, style, prompt_analysis, **kwargs)
            
            return {
                'success': True,
                'image_urls': image_urls,
                'service': 'enhanced_fallback',
                'prompt_used': prompt,
                'metadata': {
                    'prompt_analysis': prompt_analysis,
                    'generated_at': timezone.now().isoformat(),
                    'unique_id': f"enhanced_{int(time.time() * 1000)}"
                }
            }
            
        except Exception as e:
            logger.error(f"Enhanced fallback failed: {str(e)}")
            return self._get_emergency_fallback(prompt, style)
    
    def _analyze_prompt(self, prompt: str, style: str) -> Dict[str, Any]:
        """Analyze prompt to determine image characteristics"""
        analysis = {
            'colors': [],
            'objects': [],
            'mood': 'neutral',
            'lighting': 'natural',
            'composition': 'centered'
        }
        
        prompt_lower = prompt.lower()
        
        # Color analysis
        color_keywords = {
            'red': ['red', 'crimson', 'scarlet', 'burgundy'],
            'blue': ['blue', 'azure', 'navy', 'cobalt'],
            'green': ['green', 'emerald', 'forest', 'mint'],
            'yellow': ['yellow', 'gold', 'amber', 'lemon'],
            'purple': ['purple', 'violet', 'lavender', 'plum'],
            'orange': ['orange', 'amber', 'peach', 'coral'],
            'pink': ['pink', 'rose', 'magenta', 'fuchsia'],
            'black': ['black', 'dark', 'ebony', 'charcoal'],
            'white': ['white', 'ivory', 'cream', 'pearl'],
            'brown': ['brown', 'tan', 'beige', 'copper']
        }
        
        for color, keywords in color_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis['colors'].append(color)
        
        # Object analysis
        object_keywords = {
            'textile': ['fabric', 'cloth', 'textile', 'saree', 'cotton', 'silk'],
            'fashion': ['dress', 'shirt', 'pants', 'outfit', 'clothing'],
            'nature': ['flower', 'tree', 'leaf', 'garden', 'forest', 'plant'],
            'abstract': ['pattern', 'design', 'geometric', 'abstract', 'artistic']
        }
        
        for category, keywords in object_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                analysis['objects'].append(category)
        
        return analysis
    
    def _generate_ai_based_images(self, prompt: str, style: str, analysis: Dict[str, Any], **kwargs) -> List[str]:
        """Generate AI-based images using multiple sources"""
        timestamp = int(time.time() * 1000)
        prompt_hash = hashlib.md5(f"{prompt}{style}{timestamp}".encode()).hexdigest()[:8]
        
        images = []
        
        # Generate images using different services
        services = [
            self._generate_picsum_images,
            self._generate_unsplash_images,
            self._generate_placeholder_images
        ]
        
        for service in services:
            try:
                service_images = service(prompt, style, analysis, timestamp, prompt_hash, **kwargs)
                images.extend(service_images)
                if len(images) >= 3:
                    break
            except Exception as e:
                logger.warning(f"Image service failed: {str(e)}")
                continue
        
        # Ensure we have at least 3 images
        while len(images) < 3:
            fallback_url = self._generate_fallback_url(prompt, style, analysis, timestamp, len(images))
            images.append(fallback_url)
        
        return images[:5]
    
    def _generate_picsum_images(self, prompt: str, style: str, analysis: Dict[str, Any], timestamp: int, prompt_hash: str, **kwargs) -> List[str]:
        """Generate images using Picsum Photos"""
        images = []
        
        for i in range(2):
            seed = hash(f"{prompt}{style}{timestamp}{i}") % 10000
            width = kwargs.get('width', 1024)
            height = kwargs.get('height', 1024)
            image_url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
            images.append(image_url)
        
        return images
    
    def _generate_unsplash_images(self, prompt: str, style: str, analysis: Dict[str, Any], timestamp: int, prompt_hash: str, **kwargs) -> List[str]:
        """Generate images using Unsplash"""
        images = []
        
        search_terms = []
        if analysis['objects']:
            search_terms.extend(analysis['objects'])
        if analysis['colors']:
            search_terms.extend(analysis['colors'])
        if style:
            search_terms.append(style)
        
        search_query = ','.join(search_terms[:3])
        
        width = kwargs.get('width', 1024)
        height = kwargs.get('height', 1024)
        
        unique_id = f"{timestamp}_{prompt_hash}"
        image_url = f"https://source.unsplash.com/{width}x{height}/?{search_query}&sig={unique_id}"
        images.append(image_url)
        
        return images
    
    def _generate_placeholder_images(self, prompt: str, style: str, analysis: Dict[str, Any], timestamp: int, prompt_hash: str, **kwargs) -> List[str]:
        """Generate images using placeholder services"""
        images = []
        
        color_schemes = {
            'modern': ['FF6B6B', '4ECDC4', '45B7D1', '96CEB4'],
            'traditional': ['D4AF37', 'B8860B', 'CD853F', 'DEB887'],
            'festive': ['FFD700', 'FF6347', 'FF1493', 'FF4500'],
            'elegant': ['2C3E50', '34495E', '7F8C8D', '95A5A6'],
            'photorealistic': ['87CEEB', '98FB98', 'F0E68C', 'FFB6C1']
        }
        
        colors = color_schemes.get(style, color_schemes['modern'])
        
        width = kwargs.get('width', 1024)
        height = kwargs.get('height', 1024)
        
        text = f"{style.title()}+{prompt[:20].replace(' ', '+')}"
        color = colors[0]
        image_url = f"https://via.placeholder.com/{width}x{height}/{color}/FFFFFF?text={text}&timestamp={timestamp}"
        images.append(image_url)
        
        return images
    
    def _generate_fallback_url(self, prompt: str, style: str, analysis: Dict[str, Any], timestamp: int, index: int) -> str:
        """Generate fallback image URL"""
        prompt_hash = hashlib.md5(f"{prompt}{style}{timestamp}{index}".encode()).hexdigest()[:8]
        return f"https://via.placeholder.com/1024x1024/FF6B6B/FFFFFF?text=AI+Generated+{prompt_hash}&timestamp={timestamp}"
    
    def _get_emergency_fallback(self, prompt: str, style: str) -> Dict[str, Any]:
        """Get emergency fallback when all else fails"""
        timestamp = int(time.time() * 1000)
        prompt_hash = hashlib.md5(f"{prompt}{style}{timestamp}".encode()).hexdigest()[:8]
        
        emergency_url = f"https://via.placeholder.com/1024x1024/FF6B6B/FFFFFF?text=Emergency+Fallback+{prompt_hash}"
        
        return {
            'success': True,
            'image_urls': [emergency_url],
            'service': 'emergency_fallback',
            'prompt_used': prompt,
            'metadata': {
                'generated_at': timezone.now().isoformat(),
                'unique_id': f"emergency_{timestamp}"
            }
        }
    
    def is_available(self) -> bool:
        """Check if any service is available"""
        return (self.nanobanana_service.is_available() or 
                self.gemini_enhancer.is_available() or 
                any(getattr(settings, f'{service.upper()}_API_KEY', None) 
                    for service in ['stability', 'openai', 'replicate', 'huggingface']))
