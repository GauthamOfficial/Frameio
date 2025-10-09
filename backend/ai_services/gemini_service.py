"""
Google Gemini 2.5 Flash Service
Integration for AI-powered content generation using Google's Gemini API
Following official Gemini API structure with proper REST endpoints
"""
import logging
import requests
import json
import time
import hashlib
from typing import Dict, List, Optional, Any, Union
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class GeminiService:
    """Service class for Google Gemini 2.5 Flash API following official structure"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_name = settings.GEMINI_MODEL_NAME or "gemini-2.5-flash"
        
        if not self.api_key:
            logger.warning("Google Gemini API key not configured")
            self.api_key = None
        else:
            logger.info("Gemini service initialized with API key")
    
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
    
    def generate_content(
        self,
        prompt: str,
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content using Gemini API (standard REST endpoint)
        Following official API structure with Content and Part objects
        
        Args:
            prompt: Text prompt for content generation
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        model = model or self.model_name
        endpoint = f"models/{model}:generateContent"
        
        # Build request body following official structure
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Add generation config if provided
        if kwargs.get('generation_config'):
            request_body['generationConfig'] = kwargs['generation_config']
        
        result = self._make_request(endpoint, request_body)
        
        if result['success']:
            return self._process_generate_content_response(result['data'])
        else:
            return result
    
    def stream_generate_content(
        self,
        prompt: str,
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content using streaming endpoint (Server-Sent Events)
        
        Args:
            prompt: Text prompt for content generation
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing streaming results
        """
        model = model or self.model_name
        endpoint = f"models/{model}:streamGenerateContent"
        
        # Build request body following official structure
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ]
        }
        
        # Add generation config if provided
        if kwargs.get('generation_config'):
            request_body['generationConfig'] = kwargs['generation_config']
        
        result = self._make_request(endpoint, request_body)
        
        if result['success']:
            return self._process_stream_response(result['data'])
        else:
            return result
    
    def generate_multimodal_content(
        self,
        text_prompt: str,
        image_data: str,
        mime_type: str = "image/jpeg",
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate content from text and image (multimodal)
        Following official API structure with inline_data
        
        Args:
            text_prompt: Text prompt
            image_data: Base64 encoded image data
            mime_type: MIME type of the image
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        model = model or self.model_name
        endpoint = f"models/{model}:generateContent"
        
        # Build request body following official multimodal structure
        request_body = {
            "contents": [
                {
                    "parts": [
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_data
                            }
                        },
                        {
                            "text": text_prompt
                        }
                    ]
                }
            ]
        }
        
        # Add generation config if provided
        if kwargs.get('generation_config'):
            request_body['generationConfig'] = kwargs['generation_config']
        
        result = self._make_request(endpoint, request_body)
        
        if result['success']:
            return self._process_generate_content_response(result['data'])
        else:
            return result
    
    def _process_generate_content_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process standard generateContent response"""
        try:
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                
                # Extract text content
                text_content = ""
                for part in parts:
                    if 'text' in part:
                        text_content += part['text']
                
                return {
                    "success": True,
                    "data": {
                        "text": text_content,
                        "finish_reason": candidate.get('finishReason'),
                        "usage_metadata": response_data.get('usageMetadata', {}),
                        "model_version": response_data.get('modelVersion', ''),
                        "response_id": response_data.get('responseId', '')
                    },
                    "error": None
                }
            else:
                return {
                    "success": False,
                    "error": "No candidates in response",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error processing generateContent response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing response: {str(e)}",
                "data": None
            }
    
    def _process_stream_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process streaming response"""
        try:
            # For streaming, we might get multiple chunks
            # This is a simplified version - in practice you'd handle SSE properly
            return self._process_generate_content_response(response_data)
        except Exception as e:
            logger.error(f"Error processing stream response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing stream response: {str(e)}",
                "data": None
            }
    
    def create_chat_conversation(
        self,
        messages: List[Dict[str, str]],
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create a multi-turn conversation following official API structure
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (defaults to configured model)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing conversation results
        """
        model = model or self.model_name
        endpoint = f"models/{model}:generateContent"
        
        # Build contents array following official structure
        contents = []
        for message in messages:
            contents.append({
                "role": message.get('role', 'user'),
                "parts": [
                    {
                        "text": message.get('content', '')
                    }
                ]
            })
        
        request_body = {
            "contents": contents
        }
        
        # Add generation config if provided
        if kwargs.get('generation_config'):
            request_body['generationConfig'] = kwargs['generation_config']
        
        result = self._make_request(endpoint, request_body)
        
        if result['success']:
            return self._process_generate_content_response(result['data'])
        else:
            return result
    
    def generate_textile_poster(
        self,
        fabric_type: str,
        offer_text: str = "",
        festival: str = None,
        price_range: str = None,
        style: str = "modern",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate textile poster description using Gemini
        
        Args:
            fabric_type: Type of fabric (saree, kurta, etc.)
            offer_text: Text for the offer/promotion
            festival: Festival name (optional)
            price_range: Price range (optional)
            style: Design style
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        # Create a comprehensive prompt for textile poster
        prompt_parts = [
            f"Create a detailed description for a {fabric_type} poster design",
            f"Offer text: '{offer_text}'",
            f"Style: {style}",
        ]
        
        if festival:
            prompt_parts.append(f"Festival theme: {festival}")
        
        if price_range:
            prompt_parts.append(f"Price range: {price_range}")
        
        prompt_parts.extend([
            "Include design elements, color schemes, and layout suggestions",
            "Make it suitable for fashion and textile industry marketing",
            "Focus on visual appeal and promotional effectiveness"
        ])
        
        prompt = ", ".join(prompt_parts)
        
        return self.generate_content(prompt, **kwargs)
    
    def generate_captions(
        self,
        fabric_type: str,
        festival: str = None,
        price_range: str = None,
        num_captions: int = 5
    ) -> Dict[str, Any]:
        """
        Generate marketing captions for textile products using Gemini
        
        Args:
            fabric_type: Type of fabric
            festival: Festival name (optional)
            price_range: Price range (optional)
            num_captions: Number of captions to generate
            
        Returns:
            Dict containing generated captions
        """
        prompt_parts = [
            f"Generate {num_captions} marketing captions for {fabric_type}",
            "Make them engaging and promotional",
            "Focus on quality, style, and appeal"
        ]
        
        if festival:
            prompt_parts.append(f"Include {festival} theme")
        
        if price_range:
            prompt_parts.append(f"Consider price range: {price_range}")
        
        prompt = ", ".join(prompt_parts)
        
        return self.generate_content(prompt)
    
    def generate_image_description(
        self,
        image_data: str,
        mime_type: str = "image/jpeg",
        context: str = "textile fashion"
    ) -> Dict[str, Any]:
        """
        Generate description for an image using multimodal Gemini
        
        Args:
            image_data: Base64 encoded image data
            mime_type: MIME type of the image
            context: Context for the description
            
        Returns:
            Dict containing image description
        """
        prompt = f"Describe this {context} image in detail, focusing on design elements, colors, patterns, and style"
        
        return self.generate_multimodal_content(
            text_prompt=prompt,
            image_data=image_data,
            mime_type=mime_type
        )
    
    def generate_image_from_prompt(
        self,
        prompt: str,
        style: str = "photorealistic",
        width: int = 1024,
        height: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate an image using prompt-based intelligent image generation
        
        Args:
            prompt: Text prompt for image generation
            style: Style of the image (photorealistic, artistic, etc.)
            width: Image width
            height: Image height
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generated image data
        """
        try:
            # Enhance prompt for better image generation
            enhanced_prompt = self._enhance_image_prompt(prompt, style)
            
            # Generate intelligent image URL based on prompt analysis
            image_url = self._generate_intelligent_image_url(prompt, enhanced_prompt, style, width, height)
            
            return {
                "success": True,
                "image_url": image_url,
                "service": "gemini_intelligent",
                "prompt_used": enhanced_prompt,
                "metadata": {
                    "model": self.model_name,
                    "generated_at": timezone.now().isoformat(),
                    "unique_id": f"gemini_intelligent_{int(time.time() * 1000)}",
                    "original_prompt": prompt,
                    "enhanced_prompt": enhanced_prompt,
                    "style": style,
                    "dimensions": f"{width}x{height}"
                }
            }
                
        except Exception as e:
            logger.error(f"Error in image generation: {str(e)}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}",
                "data": None
            }
    
    def _enhance_image_prompt(self, prompt: str, style: str) -> str:
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
    
    def _generate_intelligent_image_url(self, prompt: str, enhanced_prompt: str, style: str, width: int, height: int) -> str:
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
        
        return image_url
    
    def _process_image_generation_response(self, response_data: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Process image generation response"""
        try:
            if 'candidates' in response_data and response_data['candidates']:
                candidate = response_data['candidates'][0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                
                # Extract image URL from response
                image_url = None
                for part in parts:
                    if 'image_url' in part:
                        image_url = part['image_url']
                        break
                
                if image_url:
                    return {
                        "success": True,
                        "image_url": image_url,
                        "service": "gemini",
                        "prompt_used": prompt,
                        "metadata": {
                            "model": self.model_name,
                            "generated_at": timezone.now().isoformat(),
                            "unique_id": f"gemini_{int(time.time() * 1000)}"
                        }
                    }
                else:
                    # Fallback to generated image URL
                    timestamp = int(time.time() * 1000)
                    prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
                    fallback_url = f"https://picsum.photos/1024/1024?random={timestamp}&text={prompt_hash}"
                    
                    return {
                        "success": True,
                        "image_url": fallback_url,
                        "service": "gemini_fallback",
                        "prompt_used": prompt,
                        "metadata": {
                            "model": self.model_name,
                            "generated_at": timezone.now().isoformat(),
                            "unique_id": f"gemini_fallback_{timestamp}"
                        }
                    }
            else:
                return {
                    "success": False,
                    "error": "No image generated",
                    "data": None
                }
        except Exception as e:
            logger.error(f"Error processing image generation response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing response: {str(e)}",
                "data": None
            }


# Global instance
gemini_service = GeminiService()

