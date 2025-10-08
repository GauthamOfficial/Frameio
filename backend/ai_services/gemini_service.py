"""
Google Gemini 2.5 Flash Image Service
Integration for AI-powered image generation using Google's Gemini API
"""
import requests
import time
import logging
import base64
import json
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class GeminiImageService:
    """Service class for Google Gemini 2.5 Flash Image generation"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        self.model_name = settings.GEMINI_MODEL_NAME
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.timeout = 60  # 60 seconds timeout
        
        if not self.api_key:
            logger.warning("Google Gemini API key not configured")
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate image using Google Gemini 2.5 Flash Image API
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Negative prompt to avoid certain elements
            width: Image width in pixels
            height: Image height in pixels
            num_images: Number of images to generate
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        if not self.api_key:
            raise ValueError("Google Gemini API key not configured")
        
        # Prepare request payload for Gemini
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Generate an image: {prompt}"
                }]
            }],
            "generationConfig": {
                "temperature": kwargs.get('temperature', 0.7),
                "topK": kwargs.get('top_k', 40),
                "topP": kwargs.get('top_p', 0.95),
                "maxOutputTokens": kwargs.get('max_tokens', 8192),
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        }
        
        # Check cache first
        cache_key = self._get_cache_key(payload)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info(f"Returning cached result for prompt: {prompt[:50]}...")
            return cached_result
        
        try:
            # Make API request to Gemini
            headers = {
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            
            logger.info(f"Making Gemini API request for prompt: {prompt[:50]}...")
            start_time = time.time()
            
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                # Process Gemini response
                processed_result = self._process_gemini_response(result, prompt, processing_time)
                
                # Cache the result
                cache.set(cache_key, processed_result, timeout=3600)  # Cache for 1 hour
                
                logger.info(f"Successfully generated image with Gemini in {processing_time:.2f}s")
                return processed_result
                
            else:
                error_msg = f"Gemini API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "data": None
                }
                
        except requests.exceptions.Timeout:
            error_msg = "Gemini API request timed out"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
        except Exception as e:
            error_msg = f"Gemini API request failed: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "data": None
            }
    
    def _process_gemini_response(self, response: Dict, prompt: str, processing_time: float) -> Dict[str, Any]:
        """Process Gemini API response"""
        try:
            # Extract generated content from Gemini response
            if 'candidates' in response and response['candidates']:
                candidate = response['candidates'][0]
                
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    
                    # Look for image data in the response
                    image_data = None
                    for part in parts:
                        if 'inlineData' in part:
                            image_data = part['inlineData']
                            break
                    
                    if image_data:
                        # Convert base64 image to URL (in real implementation, save to storage)
                        image_url = self._save_base64_image(image_data['data'], image_data.get('mimeType', 'image/png'))
                        
                        return {
                            "success": True,
                            "data": {
                                "prompt_used": prompt,
                                "generation_id": f"gemini_{int(time.time())}",
                                "model_used": self.model_name,
                                "processing_time": processing_time,
                                "image_url": image_url,
                                "image_data": image_data
                            },
                            "urls": [image_url],
                            "cost": self._calculate_gemini_cost(prompt)
                        }
                    else:
                        # If no image data, return text response
                        text_content = ""
                        for part in parts:
                            if 'text' in part:
                                text_content += part['text']
                        
                        return {
                            "success": True,
                            "data": {
                                "prompt_used": prompt,
                                "generation_id": f"gemini_{int(time.time())}",
                                "model_used": self.model_name,
                                "processing_time": processing_time,
                                "text_response": text_content
                            },
                            "urls": [],
                            "cost": self._calculate_gemini_cost(prompt)
                        }
                else:
                    return {
                        "success": False,
                        "error": "No content in Gemini response",
                        "data": None
                    }
            else:
                return {
                    "success": False,
                    "error": "No candidates in Gemini response",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"Error processing Gemini response: {str(e)}")
            return {
                "success": False,
                "error": f"Error processing response: {str(e)}",
                "data": None
            }
    
    def _save_base64_image(self, base64_data: str, mime_type: str) -> str:
        """Save base64 image data and return URL"""
        try:
            # In a real implementation, you would save this to your storage service
            # For now, we'll return a placeholder URL
            import uuid
            filename = f"gemini_{uuid.uuid4().hex[:8]}.png"
            
            # You would typically save to AWS S3, Google Cloud Storage, etc.
            # For development, we'll use a placeholder
            return f"https://example.com/generated/{filename}"
            
        except Exception as e:
            logger.error(f"Error saving base64 image: {str(e)}")
            return "https://example.com/placeholder.png"
    
    def _calculate_gemini_cost(self, prompt: str) -> float:
        """Calculate estimated cost for Gemini API usage"""
        # Gemini pricing (example rates - check current pricing)
        # Input tokens: ~$0.0005 per 1K tokens
        # Output tokens: ~$0.0015 per 1K tokens
        
        # Rough estimation based on prompt length
        input_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        output_tokens = 1000  # Estimated for image generation
        
        input_cost = (input_tokens / 1000) * 0.0005
        output_cost = (output_tokens / 1000) * 0.0015
        
        return round(input_cost + output_cost, 6)
    
    def _get_cache_key(self, payload: Dict) -> str:
        """Generate cache key for request"""
        import hashlib
        key_data = json.dumps(payload, sort_keys=True)
        return f"gemini:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def generate_textile_poster(
        self,
        fabric_type: str,
        festival: str = None,
        price_range: str = None,
        style: str = "modern",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate textile poster with Gemini
        
        Args:
            fabric_type: Type of fabric (saree, kurta, etc.)
            festival: Festival name (optional)
            price_range: Price range (optional)
            style: Design style
            **kwargs: Additional parameters
            
        Returns:
            Dict containing generation results
        """
        # Create textile-specific prompt
        prompt_parts = [
            f"Create a beautiful textile design for {fabric_type}",
            f"Style: {style}",
        ]
        
        if festival:
            prompt_parts.append(f"Festival theme: {festival}")
        
        if price_range:
            prompt_parts.append(f"Price range: {price_range}")
        
        prompt_parts.extend([
            "High quality, professional textile design",
            "Vibrant colors, intricate patterns",
            "Suitable for fashion and textile industry",
            "Clean, modern aesthetic"
        ])
        
        prompt = ", ".join(prompt_parts)
        
        return self.generate_image(
            prompt=prompt,
            width=kwargs.get('width', 1024),
            height=kwargs.get('height', 1024),
            **kwargs
        )
    
    def generate_captions(
        self,
        fabric_type: str,
        festival: str = None,
        price_range: str = None,
        num_captions: int = 5
    ) -> List[str]:
        """
        Generate marketing captions for textile products
        
        Args:
            fabric_type: Type of fabric
            festival: Festival name (optional)
            price_range: Price range (optional)
            num_captions: Number of captions to generate
            
        Returns:
            List of generated captions
        """
        if not self.api_key:
            return ["API key not configured"]
        
        prompt = f"""
        Generate {num_captions} marketing captions for {fabric_type} textile products.
        """
        
        if festival:
            prompt += f"Festival theme: {festival}. "
        
        if price_range:
            prompt += f"Price range: {price_range}. "
        
        prompt += """
        Make the captions:
        - Engaging and marketing-focused
        - Include relevant hashtags
        - Appeal to fashion-conscious customers
        - Highlight quality and style
        - Keep under 100 characters each
        
        Format as a numbered list.
        """
        
        try:
            # Use Gemini for text generation
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.8,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 1000,
                }
            }
            
            url = f"{self.base_url}/models/{self.model_name}:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and result['candidates']:
                    content = result['candidates'][0]['content']['parts'][0]['text']
                    
                    # Parse captions from response
                    captions = []
                    lines = content.split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and (line[0].isdigit() or line.startswith('-')):
                            # Remove numbering and clean up
                            caption = line.split('.', 1)[-1].strip()
                            if caption:
                                captions.append(caption)
                    
                    return captions[:num_captions]
            
            return ["Failed to generate captions"]
            
        except Exception as e:
            logger.error(f"Error generating captions: {str(e)}")
            return ["Error generating captions"]


# Global instance
gemini_service = GeminiImageService()

