"""
AI Services module for handling AI generation requests
"""
import logging
import time
import requests
from typing import Dict, List, Any, Optional
from django.conf import settings
from django.utils import timezone
from .models import AIGenerationRequest, AIUsageQuota

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIGenerationService:
    """Service class for handling AI generation requests"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.timeout = 60  # 60 seconds timeout
    
    def process_generation_request(self, request: AIGenerationRequest) -> bool:
        """
        Process an AI generation request
        
        Args:
            request: AIGenerationRequest instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Mark as processing
            request.status = 'processing'
            request.save(update_fields=['status'])
            
            start_time = time.time()
            
            # Get provider configuration
            provider = request.provider
            
            # Route to appropriate AI service
            if provider.name == 'nanobanana':
                result = self._process_nanobanana_request(request)
            elif provider.name == 'gemini':
                result = self._process_gemini_request(request)
            elif provider.name == 'openai':
                result = self._process_openai_request(request)
            elif provider.name == 'stability':
                result = self._process_stability_request(request)
            else:
                raise AIServiceError(f"Unsupported provider: {provider.name}")
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Mark as completed
            request.mark_completed(
                result_data=result.get('data', {}),
                result_urls=result.get('urls', [])
            )
            request.processing_time = processing_time
            request.cost = result.get('cost', 0)
            request.save(update_fields=['processing_time', 'cost'])
            
            # Update usage quota
            self._update_usage_quota(request)
            
            logger.info(f"Successfully processed AI request {request.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process AI request {request.id}: {str(e)}")
            request.mark_failed(str(e))
            return False
    
    def _process_nanobanana_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process NanoBanana API request"""
        try:
            import banana_dev as banana
            from django.conf import settings
            
            # Get API credentials
            api_key = settings.NANOBANANA_API_KEY
            if not api_key:
                raise AIServiceError("NanoBanana API key not configured")
            
            # Get model key from provider configuration or use default
            model_key = getattr(request.provider, 'model_key', None) or settings.NANOBANANA_MODEL_KEY
            if not model_key:
                raise AIServiceError("NanoBanana model key not configured")
            
            provider = request.provider
            
            # Prepare request data based on generation type
            if request.generation_type == 'poster':
                # Textile poster generation
                enhanced_prompt = self._enhance_textile_poster_prompt(request.prompt, request.parameters)
                payload = {
                    "text": enhanced_prompt,
                    "width": request.parameters.get('width', 1024),
                    "height": request.parameters.get('height', 1024),
                    "steps": request.parameters.get('steps', 20),
                    "guidance_scale": request.parameters.get('guidance_scale', 7.5),
                    "negative_prompt": request.negative_prompt or self._get_default_negative_prompt('poster')
                }
            elif request.generation_type == 'catalog':
                # Catalog generation with product layout
                enhanced_prompt = self._enhance_catalog_prompt(request.prompt, request.parameters)
                payload = {
                    "text": enhanced_prompt,
                    "width": request.parameters.get('width', 1200),
                    "height": request.parameters.get('height', 800),
                    "steps": request.parameters.get('steps', 25),
                    "guidance_scale": request.parameters.get('guidance_scale', 8.0),
                    "negative_prompt": request.negative_prompt or self._get_default_negative_prompt('catalog')
                }
            elif request.generation_type == 'background':
                # Background pattern generation
                enhanced_prompt = self._enhance_background_prompt(request.prompt, request.parameters)
                payload = {
                    "text": enhanced_prompt,
                    "width": request.parameters.get('width', 1024),
                    "height": request.parameters.get('height', 1024),
                    "steps": request.parameters.get('steps', 15),
                    "guidance_scale": request.parameters.get('guidance_scale', 6.0),
                    "negative_prompt": request.negative_prompt or self._get_default_negative_prompt('background')
                }
            else:
                # Default generation
                payload = {
                    "text": request.prompt,
                    **request.parameters
                }
            
            # Make API call to NanoBanana
            logger.info(f"Making NanoBanana API call for request {request.id}")
            result = banana.run(api_key, model_key, payload)
            
            # Process the response
            if result and 'modelOutputs' in result:
                model_outputs = result['modelOutputs'][0] if result['modelOutputs'] else {}
                
                # Extract generated image URLs
                image_urls = []
                if 'image_base64' in model_outputs:
                    # If base64 image is returned, we would need to save it
                    # For now, we'll assume URLs are returned
                    image_urls = model_outputs.get('image_urls', [])
                elif 'images' in model_outputs:
                    image_urls = model_outputs['images']
                
                # Calculate cost (example pricing)
                cost = self._calculate_nanobanana_cost(payload)
                
                processed_result = {
                    'data': {
                        'prompt_used': payload['text'],
                        'parameters_used': payload,
                        'generation_id': result.get('id', f"nano_{request.id}"),
                        'model_outputs': model_outputs,
                        'api_response': result
                    },
                    'urls': image_urls,
                    'cost': cost
                }
                
                logger.info(f"Successfully processed NanoBanana request {request.id}")
                return processed_result
            else:
                raise AIServiceError(f"Invalid response from NanoBanana API: {result}")
                
        except ImportError:
            logger.error("banana_dev package not installed")
            # Fallback to mock data for development
            return self._get_mock_nanobanana_result(request)
        except Exception as e:
            logger.error(f"NanoBanana API error for request {request.id}: {str(e)}")
            # For development, return mock data instead of failing
            if settings.DEBUG:
                return self._get_mock_nanobanana_result(request)
            raise AIServiceError(f"NanoBanana API error: {str(e)}")
    
    def _process_gemini_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process Google Gemini API request"""
        try:
            from .gemini_service import gemini_service
            
            # Get request parameters
            parameters = request.parameters or {}
            generation_type = request.generation_type
            
            # Route based on generation type
            if generation_type == 'poster':
                result = gemini_service.generate_textile_poster(
                    fabric_type=parameters.get('fabric_type', 'textile'),
                    festival=parameters.get('festival'),
                    price_range=parameters.get('price_range'),
                    style=parameters.get('style', 'modern'),
                    width=parameters.get('width', 1024),
                    height=parameters.get('height', 1024)
                )
            elif generation_type == 'caption':
                captions = gemini_service.generate_captions(
                    fabric_type=parameters.get('fabric_type', 'textile'),
                    festival=parameters.get('festival'),
                    price_range=parameters.get('price_range'),
                    num_captions=parameters.get('num_captions', 5)
                )
                result = {
                    "success": True,
                    "data": {
                        "captions": captions,
                        "generation_id": f"gemini_{request.id}",
                        "model_used": "gemini-2.5-flash-image"
                    },
                    "urls": [],
                    "cost": 0.001  # Estimated cost
                }
            else:
                # Generic image generation
                prompt = parameters.get('prompt', 'Generate a beautiful image')
                result = gemini_service.generate_image(
                    prompt=prompt,
                    width=parameters.get('width', 1024),
                    height=parameters.get('height', 1024)
                )
            
            if result.get('success'):
                logger.info(f"Successfully processed Gemini request {request.id}")
                return result
            else:
                raise AIServiceError(f"Gemini generation failed: {result.get('error', 'Unknown error')}")
                
        except ImportError:
            logger.error("Gemini service not available")
            # Fallback to mock data for development
            return self._get_mock_gemini_result(request)
        except Exception as e:
            logger.error(f"Gemini API error for request {request.id}: {str(e)}")
            # For development, return mock data instead of failing
            if settings.DEBUG:
                return self._get_mock_gemini_result(request)
            raise AIServiceError(f"Gemini API error: {str(e)}")
    
    def _get_mock_gemini_result(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Generate mock result for Gemini (development only)"""
        return {
            "success": True,
            "data": {
                "prompt_used": request.parameters.get('prompt', 'Mock prompt'),
                "generation_id": f"mock_gemini_{request.id}",
                "model_used": "gemini-2.5-flash-image",
                "processing_time": 2.5,
                "image_url": "https://via.placeholder.com/1024x1024/FF6B6B/FFFFFF?text=Mock+Gemini+Image"
            },
            "urls": ["https://via.placeholder.com/1024x1024/FF6B6B/FFFFFF?text=Mock+Gemini+Image"],
            "cost": 0.001
        }
    
    def _enhance_textile_poster_prompt(self, base_prompt: str, parameters: Dict) -> str:
        """Enhance prompt specifically for textile poster generation"""
        fabric_type = parameters.get('fabric_type', '')
        color_scheme = parameters.get('color_scheme', '')
        style = parameters.get('style', 'modern')
        festival = parameters.get('festival', '')
        
        enhancements = []
        
        # Add textile-specific enhancements
        if fabric_type:
            fabric_map = {
                'saree': 'elegant silk saree, traditional Indian textile',
                'cotton': 'soft cotton fabric, natural texture',
                'silk': 'luxurious silk fabric, lustrous finish',
                'linen': 'crisp linen fabric, breathable texture'
            }
            if fabric_type.lower() in fabric_map:
                enhancements.append(fabric_map[fabric_type.lower()])
        
        # Add festival themes
        if festival:
            festival_map = {
                'deepavali': 'Deepavali festival theme, golden colors, diyas, rangoli patterns',
                'pongal': 'Pongal festival theme, harvest colors, traditional motifs',
                'wedding': 'wedding celebration theme, auspicious colors, elegant design'
            }
            if festival.lower() in festival_map:
                enhancements.append(festival_map[festival.lower()])
        
        # Add color scheme
        if color_scheme:
            enhancements.append(f"color palette: {color_scheme}")
        
        # Combine with base prompt
        enhanced = f"{base_prompt}, {', '.join(enhancements)}" if enhancements else base_prompt
        enhanced += ", professional textile poster design, high quality, commercial use"
        
        return enhanced
    
    def _enhance_catalog_prompt(self, base_prompt: str, parameters: Dict) -> str:
        """Enhance prompt for catalog generation"""
        layout_style = parameters.get('layout_style', 'grid')
        product_count = parameters.get('product_count', 4)
        
        enhanced = f"{base_prompt}, {layout_style} layout catalog design"
        enhanced += f", showcasing {product_count} textile products"
        enhanced += ", clean professional layout, product catalog design, commercial quality"
        
        return enhanced
    
    def _enhance_background_prompt(self, base_prompt: str, parameters: Dict) -> str:
        """Enhance prompt for background generation"""
        pattern_type = parameters.get('pattern_type', 'seamless')
        
        enhanced = f"{base_prompt}, {pattern_type} background pattern"
        enhanced += ", textile background, seamless pattern, high resolution"
        
        return enhanced
    
    def _get_default_negative_prompt(self, generation_type: str) -> str:
        """Get default negative prompt based on generation type"""
        base_negative = "low quality, blurry, distorted, ugly, bad anatomy, watermark"
        
        type_specific = {
            'poster': "text overlay, poor typography, cluttered design",
            'catalog': "messy layout, poor product arrangement, unprofessional",
            'background': "foreground objects, text, cluttered elements"
        }
        
        if generation_type in type_specific:
            return f"{base_negative}, {type_specific[generation_type]}"
        
        return base_negative
    
    def _calculate_nanobanana_cost(self, payload: Dict) -> float:
        """Calculate cost based on NanoBanana pricing"""
        # Example pricing calculation
        base_cost = 0.05
        
        # Adjust cost based on parameters
        width = payload.get('width', 1024)
        height = payload.get('height', 1024)
        steps = payload.get('steps', 20)
        
        # Higher resolution costs more
        resolution_multiplier = (width * height) / (1024 * 1024)
        step_multiplier = steps / 20
        
        total_cost = base_cost * resolution_multiplier * step_multiplier
        return round(total_cost, 4)
    
    def _get_mock_nanobanana_result(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Get mock result for development/fallback"""
        return {
            'data': {
                'prompt_used': request.prompt,
                'parameters_used': request.parameters,
                'generation_id': f"mock_nano_{request.id}",
                'note': 'Mock data - NanoBanana API not available'
            },
            'urls': [
                f"https://mock-api.nanobanana.com/generated/{request.id}_1.png",
                f"https://mock-api.nanobanana.com/generated/{request.id}_2.png",
            ],
            'cost': 0.05
        }
    
    def _process_openai_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process OpenAI DALL-E request"""
        # Placeholder for OpenAI integration
        # TODO: Implement actual OpenAI DALL-E API integration
        
        mock_result = {
            'data': {
                'prompt_used': request.prompt,
                'model': 'dall-e-3',
                'generation_id': f"openai_{request.id}",
            },
            'urls': [
                f"https://mock-api.openai.com/generated/{request.id}.png",
            ],
            'cost': 0.08  # Mock cost
        }
        
        return mock_result
    
    def _process_stability_request(self, request: AIGenerationRequest) -> Dict[str, Any]:
        """Process Stability AI request"""
        # Placeholder for Stability AI integration
        # TODO: Implement actual Stability AI API integration
        
        mock_result = {
            'data': {
                'prompt_used': request.prompt,
                'model': 'stable-diffusion-xl',
                'generation_id': f"stability_{request.id}",
            },
            'urls': [
                f"https://mock-api.stability.ai/generated/{request.id}.png",
            ],
            'cost': 0.03  # Mock cost
        }
        
        return mock_result
    
    def _update_usage_quota(self, request: AIGenerationRequest):
        """Update usage quota for the organization"""
        try:
            # Update monthly quota
            quota, created = AIUsageQuota.objects.get_or_create(
                organization=request.organization,
                provider=request.provider,
                generation_type=request.generation_type,
                quota_type='monthly',
                defaults={
                    'max_requests': 1000,
                    'max_cost': 100.00,
                    'reset_at': timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=32)
                }
            )
            
            quota.increment_usage(cost=float(request.cost or 0))
            
        except Exception as e:
            logger.error(f"Failed to update usage quota for request {request.id}: {str(e)}")


class AIPromptEngineeringService:
    """Service for AI prompt engineering and optimization"""
    
    @staticmethod
    def enhance_textile_prompt(base_prompt: str, fabric_type: str = None, 
                             color_scheme: str = None, style: str = None) -> str:
        """
        Enhance a basic prompt for textile design generation
        
        Args:
            base_prompt: Basic prompt text
            fabric_type: Type of fabric (cotton, silk, etc.)
            color_scheme: Color scheme description
            style: Design style (modern, traditional, etc.)
            
        Returns:
            Enhanced prompt string
        """
        enhancements = []
        
        # Add fabric-specific enhancements
        if fabric_type:
            fabric_enhancements = {
                'cotton': 'soft cotton texture, natural fiber appearance',
                'silk': 'luxurious silk texture, smooth and lustrous',
                'wool': 'warm wool texture, cozy and natural',
                'linen': 'crisp linen texture, breathable and light',
                'denim': 'denim fabric texture, sturdy and casual'
            }
            if fabric_type.lower() in fabric_enhancements:
                enhancements.append(fabric_enhancements[fabric_type.lower()])
        
        # Add color scheme enhancements
        if color_scheme:
            enhancements.append(f"color palette: {color_scheme}")
        
        # Add style enhancements
        if style:
            style_enhancements = {
                'modern': 'modern design, clean lines, minimalist',
                'traditional': 'traditional patterns, classic motifs',
                'bohemian': 'bohemian style, eclectic patterns, artistic',
                'geometric': 'geometric patterns, structured design',
                'floral': 'floral motifs, natural elements, organic shapes'
            }
            if style.lower() in style_enhancements:
                enhancements.append(style_enhancements[style.lower()])
        
        # Combine base prompt with enhancements
        enhanced_prompt = base_prompt
        if enhancements:
            enhanced_prompt += f", {', '.join(enhancements)}"
        
        # Add general textile design improvements
        enhanced_prompt += ", high quality textile design, seamless pattern, professional design"
        
        return enhanced_prompt
    
    @staticmethod
    def generate_negative_prompt(generation_type: str) -> str:
        """
        Generate appropriate negative prompt based on generation type
        
        Args:
            generation_type: Type of generation (poster, catalog, etc.)
            
        Returns:
            Negative prompt string
        """
        base_negative = "low quality, blurry, distorted, ugly, bad anatomy"
        
        type_specific = {
            'poster': "text, watermark, logo, signature, low resolution",
            'catalog': "messy layout, poor composition, unorganized",
            'background': "foreground objects, text, cluttered",
            'fabric_analysis': "non-fabric materials, synthetic appearance",
            'color_palette': "muddy colors, poor color harmony"
        }
        
        if generation_type in type_specific:
            return f"{base_negative}, {type_specific[generation_type]}"
        
        return base_negative


class AIColorAnalysisService:
    """Service for AI-powered color analysis and extraction"""
    
    @staticmethod
    def extract_color_palette(image_url: str) -> List[Dict[str, Any]]:
        """
        Extract color palette from an image
        
        Args:
            image_url: URL of the image to analyze
            
        Returns:
            List of color information dictionaries
        """
        # Placeholder implementation
        # TODO: Implement actual color extraction using computer vision
        
        mock_palette = [
            {'hex': '#FF6B6B', 'rgb': [255, 107, 107], 'name': 'Coral Red', 'percentage': 35},
            {'hex': '#4ECDC4', 'rgb': [78, 205, 196], 'name': 'Turquoise', 'percentage': 25},
            {'hex': '#45B7D1', 'rgb': [69, 183, 209], 'name': 'Sky Blue', 'percentage': 20},
            {'hex': '#96CEB4', 'rgb': [150, 206, 180], 'name': 'Mint Green', 'percentage': 15},
            {'hex': '#FFEAA7', 'rgb': [255, 234, 167], 'name': 'Light Yellow', 'percentage': 5}
        ]
        
        return mock_palette
    
    @staticmethod
    def suggest_complementary_colors(base_colors: List[str]) -> List[Dict[str, Any]]:
        """
        Suggest complementary colors based on base colors
        
        Args:
            base_colors: List of hex color codes
            
        Returns:
            List of complementary color suggestions
        """
        # Placeholder implementation
        # TODO: Implement actual color theory algorithms
        
        mock_suggestions = [
            {'hex': '#FF9F43', 'name': 'Orange', 'relationship': 'complementary'},
            {'hex': '#6C5CE7', 'name': 'Purple', 'relationship': 'triadic'},
            {'hex': '#A29BFE', 'name': 'Light Purple', 'relationship': 'analogous'},
        ]
        
        return mock_suggestions
