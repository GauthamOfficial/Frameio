"""
Gemini API Integration for Prompt Enhancement
Uses Google Gemini to preprocess and enhance prompts for better image generation
"""
import os
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiPromptEnhancer:
    """Service for enhancing prompts using Google Gemini API"""
    
    def __init__(self):
        """Initialize Gemini prompt enhancer"""
        self.api_key = getattr(settings, 'GEMINI_API_KEY', None) or getattr(settings, 'GOOGLE_API_KEY', None)
        self.available = False
        
        if self.api_key and self.api_key.strip():
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.available = True
                logger.info("Gemini prompt enhancer initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {str(e)}")
                self.available = False
        else:
            logger.info("Gemini API key not configured")
    
    def enhance_prompt_for_image_generation(self, prompt: str, style: str, context: Dict[str, Any] = None) -> str:
        """
        Enhance prompt using Gemini for better image generation
        
        Args:
            prompt: Original user prompt
            style: Image style (photorealistic, artistic, etc.)
            context: Additional context (theme, objects, etc.)
            
        Returns:
            Enhanced prompt string
        """
        if not self.available:
            logger.info("Gemini not available, using local enhancement")
            return self._enhance_prompt_locally(prompt, style, context)
        
        try:
            # Create context-aware enhancement prompt
            enhancement_prompt = self._create_enhancement_prompt(prompt, style, context)
            
            # Call Gemini API
            response = self.model.generate_content(enhancement_prompt)
            enhanced = response.text.strip()
            
            if enhanced and len(enhanced) > 10:
                logger.info("Successfully enhanced prompt using Gemini")
                return enhanced
            else:
                logger.warning("Gemini returned empty or invalid response")
                return self._enhance_prompt_locally(prompt, style, context)
                
        except Exception as e:
            logger.warning(f"Gemini enhancement failed: {str(e)}")
            return self._enhance_prompt_locally(prompt, style, context)
    
    def _create_enhancement_prompt(self, prompt: str, style: str, context: Dict[str, Any] = None) -> str:
        """Create enhancement prompt for Gemini"""
        context_info = ""
        if context:
            context_info = f"\nAdditional context: {context}"
        
        enhancement_prompt = f"""
You are an expert AI image generation prompt engineer. Your task is to enhance the following prompt for optimal image generation results.

Original prompt: "{prompt}"
Style: {style}
{context_info}

Requirements for enhancement:
1. Make the prompt more specific and detailed
2. Add relevant technical photography terms
3. Include style-specific enhancements
4. Add quality descriptors (high resolution, sharp focus, professional quality)
5. Include lighting and composition details
6. Add relevant artistic or technical terms
7. Keep it under 200 words
8. Make it suitable for AI image generation
9. Ensure the enhanced prompt will produce images that match the original intent

Style-specific guidelines:
- photorealistic: Add terms like "professional photography", "sharp focus", "high resolution", "detailed"
- artistic: Add terms like "artistic style", "creative composition", "stylized", "artistic interpretation"
- textile: Add terms like "textile design", "fabric texture", "fashion photography", "garment focus"
- modern: Add terms like "modern design", "contemporary style", "clean lines", "minimalist"
- traditional: Add terms like "traditional patterns", "classic design", "heritage style", "cultural elements"

Return only the enhanced prompt, no explanations or additional text.
"""
        return enhancement_prompt
    
    def _enhance_prompt_locally(self, prompt: str, style: str, context: Dict[str, Any] = None) -> str:
        """Local prompt enhancement when Gemini is not available"""
        enhancements = []
        
        # Style-specific enhancements
        style_enhancements = {
            'photorealistic': [
                'high resolution', 'detailed', 'professional photography',
                'sharp focus', 'well lit', 'crystal clear', 'ultra detailed'
            ],
            'artistic': [
                'artistic style', 'creative composition', 'stylized',
                'artistic interpretation', 'creative design', 'artistic vision'
            ],
            'textile': [
                'textile design', 'fabric pattern', 'fashion photography',
                'textile focus', 'fabric texture', 'garment design', 'fashion style'
            ],
            'modern': [
                'modern design', 'contemporary style', 'clean lines',
                'minimalist aesthetic', 'sleek design', 'contemporary art'
            ],
            'traditional': [
                'traditional patterns', 'classic design', 'heritage style',
                'cultural elements', 'traditional motifs', 'classic art'
            ],
            'festive': [
                'festive colors', 'celebration theme', 'joyful atmosphere',
                'special occasion', 'festive design', 'celebration style'
            ],
            'elegant': [
                'elegant design', 'sophisticated style', 'luxury feel',
                'refined aesthetics', 'elegant composition', 'sophisticated art'
            ]
        }
        
        # Add style-specific enhancements
        if style in style_enhancements:
            enhancements.extend(style_enhancements[style])
        
        # Add context-based enhancements
        if context:
            if 'colors' in context and context['colors']:
                color_desc = ', '.join(context['colors'])
                enhancements.append(f"{color_desc} color scheme")
            
            if 'objects' in context and context['objects']:
                object_desc = ', '.join(context['objects'])
                enhancements.append(f"{object_desc} focus")
            
            if 'mood' in context and context['mood']:
                enhancements.append(f"{context['mood']} mood")
        
        # Add general quality enhancements
        enhancements.extend([
            'high quality', 'professional', 'detailed', 'sharp',
            'well composed', 'beautiful', 'stunning', 'excellent quality'
        ])
        
        # Add lighting enhancements
        lighting_enhancements = [
            'soft lighting', 'natural lighting', 'well lit',
            'professional lighting', 'optimal lighting'
        ]
        enhancements.extend(lighting_enhancements)
        
        # Combine prompt with enhancements
        enhanced = f"{prompt}, {', '.join(enhancements)}"
        
        # Add negative prompt elements
        negative_elements = [
            'blurry', 'low quality', 'distorted', 'watermark',
            'text overlay', 'poor lighting', 'bad composition',
            'pixelated', 'grainy', 'out of focus'
        ]
        enhanced += f", avoid: {', '.join(negative_elements)}"
        
        return enhanced
    
    def generate_style_specific_prompt(self, base_prompt: str, style: str, theme: str = None) -> str:
        """Generate style-specific prompt for different themes"""
        if not self.available:
            return self._generate_style_prompt_locally(base_prompt, style, theme)
        
        try:
            style_prompt = f"""
Create a detailed, style-specific prompt for AI image generation.

Base prompt: "{base_prompt}"
Style: {style}
Theme: {theme or 'general'}

Create a prompt that:
1. Incorporates the base prompt naturally
2. Emphasizes the {style} style
3. Includes theme-specific elements if theme is provided
4. Adds appropriate technical terms for the style
5. Ensures high-quality image generation
6. Keeps it under 150 words

Return only the enhanced prompt.
"""
            
            response = self.model.generate_content(style_prompt)
            enhanced = response.text.strip()
            
            if enhanced and len(enhanced) > 10:
                return enhanced
            else:
                return self._generate_style_prompt_locally(base_prompt, style, theme)
                
        except Exception as e:
            logger.warning(f"Gemini style prompt generation failed: {str(e)}")
            return self._generate_style_prompt_locally(base_prompt, style, theme)
    
    def _generate_style_prompt_locally(self, base_prompt: str, style: str, theme: str = None) -> str:
        """Generate style-specific prompt locally"""
        style_descriptions = {
            'photorealistic': 'high-resolution, detailed, professional photography, sharp focus, realistic',
            'artistic': 'artistic style, creative composition, stylized, artistic interpretation',
            'textile': 'textile design, fabric pattern, fashion photography, textile focus',
            'modern': 'modern design, contemporary style, clean lines, minimalist aesthetic',
            'traditional': 'traditional patterns, classic design, heritage style, cultural elements',
            'festive': 'festive colors, celebration theme, joyful atmosphere, special occasion',
            'elegant': 'elegant design, sophisticated style, luxury feel, refined aesthetics'
        }
        
        style_desc = style_descriptions.get(style, 'high quality, detailed')
        
        if theme:
            enhanced = f"{base_prompt}, {style_desc}, {theme} theme, professional quality, detailed"
        else:
            enhanced = f"{base_prompt}, {style_desc}, professional quality, detailed"
        
        return enhanced
    
    def is_available(self) -> bool:
        """Check if Gemini service is available"""
        return self.available
