"""
Branding Kit AI Service
Service for generating branding assets using Gemini API
"""
import os
import logging
import base64
from typing import Dict, Any, List, Optional
from django.conf import settings
from PIL import Image
from io import BytesIO

try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    genai = None
    types = None

logger = logging.getLogger(__name__)


class BrandingKitService:
    """
    Service for generating branding assets using Gemini API
    """
    
    def __init__(self):
        """Initialize the branding kit service"""
        self.api_key = os.getenv("GEMINI_API_KEY") or getattr(settings, 'GEMINI_API_KEY', None)
        self.client = None
        
        if not GENAI_AVAILABLE:
            logger.error("Google GenAI library not available")
            return
            
        if not self.api_key:
            logger.error("GEMINI_API_KEY not configured")
            return
            
        try:
            self.client = genai.Client(api_key=self.api_key)
            logger.info("Branding Kit service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {str(e)}")
            self.client = None
    
    def generate_logo(self, prompt: str, style: str = "modern") -> Dict[str, Any]:
        """
        Generate a logo based on the prompt
        
        Args:
            prompt: Description of the logo
            style: Style preference (modern, vintage, minimalist, etc.)
            
        Returns:
            Dict containing logo data and metadata
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Gemini client not available'
            }
        
        try:
            # Enhanced prompt for logo generation
            enhanced_prompt = f"""
            Create a professional logo for: {prompt}
            
            Style: {style}
            Requirements:
            - Clean, scalable design
            - Works on both light and dark backgrounds
            - Professional appearance
            - Simple and memorable
            - High contrast for readability
            - Vector-style design
            - No complex details that won't scale
            - Modern typography if text is included
            
            The logo should be centered and well-composed.
            """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=enhanced_prompt
            )
            
            # Extract image data
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if not image_parts:
                return {
                    'success': False,
                    'error': 'No image generated'
                }
            
            # Convert to PIL Image
            image = Image.open(BytesIO(image_parts[0]))
            
            # Convert to base64 for API response
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                'success': True,
                'logo': {
                    'data': img_str,
                    'format': 'PNG',
                    'width': image.width,
                    'height': image.height
                },
                'prompt': prompt,
                'style': style
            }
            
        except Exception as e:
            logger.error(f"Error generating logo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_color_palette(self, prompt: str, num_colors: int = 5) -> Dict[str, Any]:
        """
        Generate a color palette based on the prompt
        
        Args:
            prompt: Description of the brand/design
            num_colors: Number of colors to generate
            
        Returns:
            Dict containing color palette data
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Gemini client not available'
            }
        
        try:
            # Enhanced color detection with more comprehensive keywords
            color_keywords = [
                'blue', 'red', 'green', 'yellow', 'purple', 'orange', 'pink', 'brown', 'black', 'white', 
                'gray', 'grey', 'gold', 'silver', 'navy', 'teal', 'coral', 'maroon', 'beige', 'cream',
                'cyan', 'magenta', 'lime', 'indigo', 'violet', 'turquoise', 'amber', 'crimson', 'emerald',
                'sapphire', 'ruby', 'pearl', 'bronze', 'copper', 'platinum', 'charcoal', 'ivory', 'tan',
                'burgundy', 'forest green', 'sky blue', 'royal blue', 'deep blue', 'light blue', 'dark blue',
                'bright red', 'deep red', 'light green', 'dark green', 'bright yellow', 'dark yellow',
                'hot pink', 'deep pink', 'light pink', 'dark purple', 'light purple', 'bright orange',
                'dark orange', 'light brown', 'dark brown', 'light gray', 'dark gray', 'steel blue',
                'olive green', 'mint green', 'lavender', 'rose gold', 'champagne', 'coffee', 'chocolate'
            ]
            
            # Find mentioned colors in the prompt
            prompt_lower = prompt.lower()
            mentioned_colors = [color for color in color_keywords if color.lower() in prompt_lower]
            
            # Also check for hex codes and RGB values
            import re
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', prompt)
            rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', prompt)
            
            logger.info(f"Detected colors in prompt: {mentioned_colors}")
            logger.info(f"Detected hex colors: {hex_colors}")
            logger.info(f"Detected RGB colors: {rgb_colors}")
            
            if mentioned_colors or hex_colors or rgb_colors:
                # Use the colors mentioned in the prompt
                color_specifications = []
                if mentioned_colors:
                    color_specifications.append(f"Use these specific colors: {', '.join(mentioned_colors)}")
                if hex_colors:
                    color_specifications.append(f"Use these hex colors: {', '.join(hex_colors)}")
                if rgb_colors:
                    color_specifications.append(f"Use these RGB colors: {', '.join(rgb_colors)}")
                
                enhanced_prompt = f"""
                Create a professional color palette for a brand with these exact specifications:
                {'. '.join(color_specifications)}
                
                IMPORTANT: The color palette MUST prominently feature these exact colors. Do not change or modify them.
                
                Generate a cohesive color palette that includes:
                - The specified colors as the primary colors
                - Complementary colors that harmonize with the specified colors
                - Neutral colors (grays, whites, blacks) for balance
                - Ensure the specified colors are the most prominent in the palette
                
                Present the colors in a clean, organized palette with the specified colors clearly visible and dominant.
                """
            else:
                # Generate colors based on the brand description
                enhanced_prompt = f"""
                Create a color palette for: {prompt}
                
                Generate {num_colors} colors that work well together for a brand.
                Include:
                - Primary brand color
                - Secondary colors
                - Accent colors
                - Neutral colors
                
                The colors should be:
                - Harmonious and professional
                - Suitable for both digital and print
                - Accessible and readable
                - Modern and contemporary
                
                Present the colors as a clean, organized palette.
                """
            
            response = self.client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=enhanced_prompt
            )
            
            # Extract image data
            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]
            
            if not image_parts:
                return {
                    'success': False,
                    'error': 'No color palette generated'
                }
            
            # Convert to PIL Image
            image = Image.open(BytesIO(image_parts[0]))
            
            # Convert to base64 for API response
            buffered = BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            return {
                'success': True,
                'palette': {
                    'data': img_str,
                    'format': 'PNG',
                    'width': image.width,
                    'height': image.height
                },
                'prompt': prompt,
                'num_colors': num_colors,
                'used_colors': mentioned_colors if mentioned_colors else []
            }
            
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_branding_kit(self, prompt: str, style: str = "modern") -> Dict[str, Any]:
        """
        Generate a complete branding kit including logo and color palette
        
        Args:
            prompt: Description of the brand
            style: Style preference
            
        Returns:
            Dict containing complete branding kit
        """
        if not self.client:
            return {
                'success': False,
                'error': 'Gemini client not available'
            }
        
        try:
            # Generate logo
            logo_result = self.generate_logo(prompt, style)
            if not logo_result.get('success'):
                return logo_result
            
            # Generate color palette using the same prompt to maintain color consistency
            palette_result = self.generate_color_palette(prompt)
            if not palette_result.get('success'):
                return palette_result
            
            return {
                'success': True,
                'branding_kit': {
                    'logo': logo_result['logo'],
                    'color_palette': palette_result['palette']
                },
                'prompt': prompt,
                'style': style,
                'used_colors': palette_result.get('used_colors', []),
                'generated_at': str(os.getenv('TIMESTAMP', 'unknown'))
            }
            
        except Exception as e:
            logger.error(f"Error generating branding kit: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        return self.client is not None and GENAI_AVAILABLE
