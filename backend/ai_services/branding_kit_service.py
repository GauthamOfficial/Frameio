"""
Branding Kit AI Service
Service for generating branding assets using Gemini API
"""
import os
import logging
import re
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
    
    def generate_color_palette_from_logo(self, logo_base64: str, num_colors: int = 5, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a labeled color palette image extracted from a provided logo (base64 PNG/JPEG).
        Returns the swatch image and list of extracted hex colors.
        """
        try:
            if not logo_base64:
                return {
                    'success': False,
                    'error': 'Logo image data is required'
                }

            image_bytes = base64.b64decode(logo_base64)
            image = Image.open(BytesIO(image_bytes)).convert('RGBA')

            hex_colors, _ = self._extract_palette_image(image, max(1, int(num_colors)))

            labeled_image = self._render_labeled_palette(title, hex_colors)

            buffered = BytesIO()
            labeled_image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            return {
                'success': True,
                'palette': {
                    'data': img_str,
                    'format': 'PNG',
                    'width': labeled_image.width,
                    'height': labeled_image.height,
                    'colors': hex_colors
                },
                'num_colors': len(hex_colors),
                'generation_method': 'logo_extraction'
            }
        except Exception as e:
            logger.error(f"Error generating palette from logo: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_palette_image(self, image: Image.Image, num_colors: Optional[int]) -> (List[str], Image.Image):
        """
        Extract dominant colors from an image using adaptive quantization.
        Returns a list of hex colors and a simple swatch image.
        """
        from PIL import Image as PILImage
        from PIL import ImageDraw

        max_side = 256
        w, h = image.size
        scale = min(1.0, max_side / float(max(w, h)) if max(w, h) > 0 else 1.0)
        image_small = image.resize((max(1, int(w * scale)), max(1, int(h * scale))), PILImage.LANCZOS) if scale < 1.0 else image

        if image_small.mode != 'RGBA':
            image_small = image_small.convert('RGBA')
        white_bg = PILImage.new('RGBA', image_small.size, (255, 255, 255, 255))
        image_opaque = PILImage.alpha_composite(white_bg, image_small)

        initial_palette_size = 128
        quantized = image_opaque.convert('RGB').convert('P', palette=PILImage.ADAPTIVE, colors=initial_palette_size)

        palette = quantized.getpalette()
        color_counts = quantized.getcolors() or []

        index_to_rgb = []
        for i in range(0, len(palette), 3):
            r, g, b = palette[i:i+3]
            index_to_rgb.append((r, g, b))

        freq_by_rgb = {}
        for count, idx in color_counts:
            if idx < len(index_to_rgb):
                rgb = index_to_rgb[idx]
                freq_by_rgb[rgb] = freq_by_rgb.get(rgb, 0) + count

        sorted_rgbs = sorted(freq_by_rgb.items(), key=lambda x: x[1], reverse=True)

        def rgb_to_hsv(r: int, g: int, b: int):
            import colorsys
            return colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)

        def is_near_gray(r: int, g: int, b: int, delta: int = 15) -> bool:
            return abs(r-g) < delta and abs(r-b) < delta and abs(g-b) < delta

        def is_near_white(r: int, g: int, b: int, thr: int = 240) -> bool:
            return r >= thr and g >= thr and b >= thr

        def is_near_black(r: int, g: int, b: int, thr: int = 20) -> bool:
            return r <= thr and g <= thr and b <= thr

        # Filter to keep important colors but be less aggressive
        filtered: List[tuple] = []
        for rgb, cnt in sorted_rgbs:
            r, g, b = rgb
            # Only exclude pure white and pure black
            if is_near_white(r, g, b) or is_near_black(r, g, b):
                continue
            h, s, v = rgb_to_hsv(r, g, b)
            # Accept more colors - lower saturation threshold
            if is_near_gray(r, g, b) and s < 0.08:  # Only exclude very gray colors
                continue
            filtered.append((rgb, cnt))

        # If filtering removed everything, use top colors by frequency
        if not filtered:
            filtered = sorted_rgbs[:min(10, len(sorted_rgbs))]

        # Deduplicate similar colors with wider threshold for more variety
        deduped: List[tuple] = []
        SIMILARITY_THRESHOLD = 35.0
        for rgb, cnt in filtered:
            if not any(((rgb[0]-kr)**2 + (rgb[1]-kg)**2 + (rgb[2]-kb)**2) ** 0.5 < SIMILARITY_THRESHOLD for (kr, kg, kb), _ in deduped):
                deduped.append((rgb, cnt))

        selected_rgbs = [rgb for rgb, _ in deduped][:max(1, int(num_colors))] if num_colors is not None else [rgb for rgb, _ in deduped]

        hex_colors = [f"#{r:02x}{g:02x}{b:02x}" for (r, g, b) in selected_rgbs]

        section_width = 120
        section_height = 120
        total_width = section_width * len(hex_colors)
        total_height = section_height
        swatch = PILImage.new('RGB', (total_width, total_height), 'white')
        draw = ImageDraw.Draw(swatch)
        for i, hex_color in enumerate(hex_colors):
            x1 = i * section_width
            x2 = x1 + section_width
            draw.rectangle([x1, 0, x2, section_height], fill=hex_color)
            draw.rectangle([x1, 0, x2, section_height], outline='black', width=2)

        return hex_colors, swatch

    def _render_labeled_palette(self, title: Optional[str], hex_colors: List[str]) -> Image.Image:
        """
        Render a 1:1 square palette with title and color swatches with hex codes.
        """
        from PIL import Image as PILImage
        from PIL import ImageDraw, ImageFont

        # Use all extracted colors (not just 5)
        colors = hex_colors if hex_colors else ['#CCCCCC']
        num = len(colors)

        # Create 1:1 square canvas (1024x1024)
        canvas_size = 1024
        img = PILImage.new('RGB', (canvas_size, canvas_size), color='#EFEFEF')
        draw = ImageDraw.Draw(img)

        # Load fonts with fallback
        try:
            font_title = ImageFont.truetype("arial.ttf", 52)
            font_hex = ImageFont.truetype("arial.ttf", 22)
        except Exception:
            try:
                # Try alternative font paths for different OS
                font_title = ImageFont.truetype("Arial.ttf", 52)
                font_hex = ImageFont.truetype("Arial.ttf", 22)
            except Exception:
                font_title = ImageFont.load_default()
                font_hex = ImageFont.load_default()

        # Title: "Color Palette" only
        title_text = 'Color Palette'
        title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]
        title_y = 100
        draw.text(((canvas_size - title_w) / 2, title_y), title_text, fill='#1a1a1a', font=font_title)

        # Calculate swatch layout - use full width efficiently
        margin_x = 60
        swatch_gap = 20
        available_width = canvas_size - (2 * margin_x)
        swatch_size = int((available_width - (num - 1) * swatch_gap) / num)
        
        # Ensure reasonable swatch size
        if swatch_size > 180:
            swatch_size = 180
            total_swatches_width = num * swatch_size + (num - 1) * swatch_gap
            start_x = (canvas_size - total_swatches_width) / 2
        else:
            start_x = margin_x
        
        # Position swatches in center of remaining space
        header_space = title_y + title_h + 80
        footer_space = 100
        available_vertical = canvas_size - header_space - footer_space
        swatches_start_y = header_space + (available_vertical - swatch_size - 60) / 2

        # Draw color swatches and hex codes
        for i, hex_color in enumerate(colors):
            x1 = start_x + i * (swatch_size + swatch_gap)
            y1 = swatches_start_y
            x2 = x1 + swatch_size
            y2 = y1 + swatch_size
            
            # Draw color swatch
            draw.rectangle([x1, y1, x2, y2], fill=hex_color, outline='#2a2a2a', width=3)

            # Hex code centered below swatch
            hex_text = hex_color.upper()
            hex_bbox = draw.textbbox((0, 0), hex_text, font=font_hex)
            hex_w = hex_bbox[2] - hex_bbox[0]
            hex_y = y2 + 25
            hex_x = x1 + (swatch_size - hex_w) / 2
            draw.text((hex_x, hex_y), hex_text, fill='#333333', font=font_hex)

        return img

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
            # Graceful fallback: generate a simple placeholder logo and palette
            try:
                from PIL import Image as PILImage
                from PIL import ImageDraw, ImageFont
                # Create a simple placeholder logo (512x512) with first letter
                canvas_size = 512
                bg_color = (240, 240, 240)
                text_color = (26, 26, 26)
                img = PILImage.new('RGB', (canvas_size, canvas_size), color=bg_color)
                draw = ImageDraw.Draw(img)
                letter = (prompt.strip()[:1] or 'F').upper()
                try:
                    font = ImageFont.truetype("arial.ttf", 220)
                except Exception:
                    try:
                        font = ImageFont.truetype("Arial.ttf", 220)
                    except Exception:
                        font = ImageFont.load_default()
                bbox = draw.textbbox((0, 0), letter, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                draw.text(((canvas_size - text_w) / 2, (canvas_size - text_h) / 2), letter, fill=text_color, font=font)

                buffered_logo = BytesIO()
                img.save(buffered_logo, format="PNG")
                logo_b64 = base64.b64encode(buffered_logo.getvalue()).decode()

                palette_result = self.generate_color_palette_from_logo(logo_b64, 5, title=prompt)
                if not palette_result.get('success'):
                    # Fallback to programmatic default palette
                    prog_palette = self._create_programmatic_palette(['blue', 'green', 'purple', 'orange', 'pink'], [], [])
                    buffered = BytesIO()
                    prog_palette.save(buffered, format="PNG")
                    palette_b64 = base64.b64encode(buffered.getvalue()).decode()
                    palette_payload = {
                        'data': palette_b64,
                        'format': 'PNG',
                        'width': prog_palette.width,
                        'height': prog_palette.height,
                        'colors': ['#0000FF', '#00FF00', '#800080', '#FFA500', '#FFC0CB'],
                    }
                else:
                    palette_payload = palette_result['palette']

                return {
                    'success': True,
                    'branding_kit': {
                        'logo': {
                            'data': logo_b64,
                            'format': 'PNG',
                            'width': img.width,
                            'height': img.height,
                        },
                        'color_palette': palette_payload,
                    },
                    'prompt': prompt,
                    'style': style,
                    'used_colors': palette_payload.get('colors', []),
                    'generated_at': str(os.getenv('TIMESTAMP', 'fallback')),
                    'fallback': True,
                    'message': 'Generated using local fallback (Gemini unavailable)'
                }
            except Exception as e:
                logger.error(f"Fallback branding kit generation failed: {str(e)}")
                return {
                    'success': False,
                    'error': 'Gemini client not available and fallback failed'
                }
        
        try:
            # Generate logo
            logo_result = self.generate_logo(prompt, style)
            if not logo_result.get('success'):
                return logo_result
            
            # Generate primary color palette from the generated logo image
            palette_result = self.generate_color_palette_from_logo(
                logo_result['logo']['data'],
                5,
                title=prompt
            )
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
                'used_colors': palette_result['palette'].get('colors', []),
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
