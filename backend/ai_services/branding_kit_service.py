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
        Generate a color palette based on the prompt using programmatic generation
        
        Args:
            prompt: Description of the brand/design
            num_colors: Number of colors to generate
            
        Returns:
            Dict containing color palette data
        """
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
            
            # Check for common color combinations
            color_combinations = [
                'red and white', 'blue and white', 'green and white', 'black and white',
                'red and black', 'blue and red', 'green and blue', 'yellow and black',
                'purple and white', 'orange and white', 'pink and white', 'gray and white'
            ]
            
            for combo in color_combinations:
                if combo in prompt_lower:
                    # Split the combination and add individual colors
                    colors_in_combo = combo.split(' and ')
                    for color in colors_in_combo:
                        if color.strip() not in mentioned_colors:
                            mentioned_colors.append(color.strip())
            
            # Also check for hex codes and RGB values
            import re
            hex_colors = re.findall(r'#[0-9a-fA-F]{6}', prompt)
            rgb_colors = re.findall(r'rgb\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*\)', prompt)
            
            logger.info(f"Detected colors in prompt: {mentioned_colors}")
            logger.info(f"Detected hex colors: {hex_colors}")
            logger.info(f"Detected RGB colors: {rgb_colors}")
            logger.info(f"Original prompt: {prompt}")
            
            # ALWAYS use programmatic color palette generation for strict control
            if mentioned_colors or hex_colors or rgb_colors:
                logger.info(f"Using mentioned colors: {mentioned_colors}")
                # Generate palette using only the mentioned colors
                palette_image = self._create_programmatic_palette(mentioned_colors, hex_colors, rgb_colors)
            else:
                logger.info("No specific colors detected, using default colors")
                # Generate a default palette if no specific colors mentioned
                default_colors = ['blue', 'green', 'purple', 'orange', 'pink']
                palette_image = self._create_programmatic_palette(default_colors[:num_colors], [], [])
            
            # Convert to base64 for API response
            buffered = BytesIO()
            palette_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            logger.info(f"Programmatic color palette generated with mentioned colors: {mentioned_colors}")
            
            return {
                'success': True,
                'palette': {
                    'data': img_str,
                    'format': 'PNG',
                    'width': palette_image.width,
                    'height': palette_image.height
                },
                'prompt': prompt,
                'num_colors': len(mentioned_colors) if mentioned_colors else 5,
                'used_colors': mentioned_colors if mentioned_colors else [],
                'strict_mode': True,  # Indicates strict color adherence
                'instructions': f'Only these colors included: {", ".join(mentioned_colors)}',
                'original_prompt': prompt,
                'detected_colors': mentioned_colors,
                'generation_method': 'programmatic'
            }
            
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_programmatic_palette(self, mentioned_colors: list, hex_colors: list, rgb_colors: list) -> Image.Image:
        """
        Create a color palette programmatically using only the specified colors
        """
        from PIL import Image, ImageDraw, ImageFont
        
        # Color mapping for mentioned colors
        color_map = {
            'blue': '#0000FF', 'red': '#FF0000', 'green': '#00FF00', 'yellow': '#FFFF00',
            'purple': '#800080', 'orange': '#FFA500', 'pink': '#FFC0CB', 'brown': '#A52A2A',
            'black': '#000000', 'white': '#FFFFFF', 'gray': '#808080', 'grey': '#808080',
            'gold': '#FFD700', 'silver': '#C0C0C0', 'navy': '#000080', 'teal': '#008080',
            'coral': '#FF7F50', 'maroon': '#800000', 'beige': '#F5F5DC', 'cream': '#FFFDD0',
            'cyan': '#00FFFF', 'magenta': '#FF00FF', 'lime': '#00FF00', 'indigo': '#4B0082',
            'violet': '#8A2BE2', 'turquoise': '#40E0D0', 'amber': '#FFBF00', 'crimson': '#DC143C',
            'emerald': '#50C878', 'sapphire': '#0F52BA', 'ruby': '#E0115F', 'pearl': '#F8F6F0',
            'bronze': '#CD7F32', 'copper': '#B87333', 'platinum': '#E5E4E2', 'charcoal': '#36454F',
            'ivory': '#FFFFF0', 'tan': '#D2B48C', 'burgundy': '#800020', 'forest green': '#228B22',
            'sky blue': '#87CEEB', 'royal blue': '#4169E1', 'deep blue': '#000080', 'light blue': '#ADD8E6',
            'dark blue': '#00008B', 'bright red': '#FF0000', 'deep red': '#8B0000', 'light green': '#90EE90',
            'dark green': '#006400', 'bright yellow': '#FFFF00', 'dark yellow': '#B8860B',
            'hot pink': '#FF69B4', 'deep pink': '#FF1493', 'light pink': '#FFB6C1', 'dark purple': '#663399',
            'light purple': '#DDA0DD', 'bright orange': '#FFA500', 'dark orange': '#FF8C00',
            'light brown': '#D2B48C', 'dark brown': '#8B4513', 'light gray': '#D3D3D3', 'dark gray': '#A9A9A9',
            'steel blue': '#4682B4', 'olive green': '#808000', 'mint green': '#98FB98', 'lavender': '#E6E6FA',
            'rose gold': '#E8B4B8', 'champagne': '#F7E7CE', 'coffee': '#6F4E37', 'chocolate': '#7B3F00'
        }
        
        # Collect all colors to use
        colors_to_use = []
        
        # Add mentioned colors
        for color in mentioned_colors:
            if color.lower() in color_map:
                colors_to_use.append(color_map[color.lower()])
        
        # Add hex colors
        colors_to_use.extend(hex_colors)
        
        # Add RGB colors (convert to hex)
        for rgb in rgb_colors:
            # Extract RGB values
            rgb_values = re.findall(r'\d+', rgb)
            if len(rgb_values) == 3:
                r, g, b = map(int, rgb_values)
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors_to_use.append(hex_color)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_colors = []
        for color in colors_to_use:
            if color not in seen:
                seen.add(color)
                unique_colors.append(color)
        
        logger.info(f"Colors to use in palette: {unique_colors}")
        
        if not unique_colors:
            # Fallback to default colors
            unique_colors = ['#0000FF', '#00FF00', '#FF0000', '#FFFF00', '#800080']
            logger.info(f"Using fallback colors: {unique_colors}")
        
        logger.info(f"Final colors for palette: {unique_colors}")
        
        # Create the palette image
        num_colors = len(unique_colors)
        section_width = 200
        section_height = 100
        total_width = section_width * num_colors
        total_height = section_height
        
        # Create image with white background
        img = Image.new('RGB', (total_width, total_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw color sections
        for i, color in enumerate(unique_colors):
            x1 = i * section_width
            y1 = 0
            x2 = x1 + section_width
            y2 = section_height
            
            # Draw the color rectangle
            draw.rectangle([x1, y1, x2, y2], fill=color)
            
            # Add a border
            draw.rectangle([x1, y1, x2, y2], outline='black', width=2)
        
        return img
    
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
