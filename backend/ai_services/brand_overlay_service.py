"""
Brand Overlay Service for AI-Generated Posters
Handles adding company branding (logo and contact info) to AI-generated poster images.
"""
import os
import time
import logging
import math
from typing import Dict, Any, Optional, Tuple, List
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import uuid
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class BrandOverlayService:
    """
    Service for adding brand overlays to AI-generated poster images.
    """
    
    def __init__(self):
        """Initialize the brand overlay service."""
        self.default_font_size = 24
        self.logo_size = (150, 150)  # Decreased from (200, 200)
        self.contact_font_size = 22
        self.margin = 30
        
    def add_brand_overlay(self, 
                         poster_path: str, 
                         company_profile, 
                         output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Add brand overlay to AI-generated poster.
        
        Args:
            poster_path: Path to the AI-generated poster image
            company_profile: CompanyProfile instance with branding info
            output_filename: Optional custom filename for output
            
        Returns:
            Dict containing status and final image path
        """
        try:
            if not company_profile:
                return {"status": "error", "message": "Company profile not found"}
            
            # Load the poster image
            poster_image = self._load_image(poster_path)
            if not poster_image:
                return {"status": "error", "message": "Failed to load poster image"}
            
            # Convert to RGBA for transparency support
            poster_image = poster_image.convert("RGBA")
            
            # Add logo overlay
            logo_metadata = None
            if company_profile.logo:
                poster_image, logo_metadata = self._add_logo_overlay(poster_image, company_profile)
            
            # Add contact information overlay
            contact_info = company_profile.get_contact_info()
            contact_metadata = None
            if contact_info:
                poster_image, contact_metadata = self._add_contact_overlay(poster_image, contact_info, company_profile)
            
            # Auto-trim any uniform white borders introduced by generation
            try:
                poster_image = self._trim_uniform_borders(poster_image)
            except Exception as e:
                logger.debug(f"Border trim skipped: {e}")

            # Save the final image
            final_path = self._save_final_image(poster_image, output_filename)
            
            if final_path:
                logger.info(f"Brand overlay added successfully: {final_path}")
                return {
                    "status": "success",
                    "image_path": final_path,
                    "image_url": default_storage.url(final_path),
                    "branding_applied": True,
                    "logo_added": bool(company_profile.logo),
                    "contact_info_added": bool(contact_info),
                    "branding_metadata": {
                        "logo": logo_metadata,
                        "contact": contact_metadata
                    }
                }
            else:
                return {"status": "error", "message": "Failed to save final image"}
                
        except Exception as e:
            logger.error(f"Error adding brand overlay: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _trim_uniform_borders(self, image: Image.Image, threshold: int = 245, max_border_ratio: float = 0.2) -> Image.Image:
        """
        Remove uniform near-white borders around the image without adding padding.
        - threshold: pixel is considered background if all RGB >= threshold
        - max_border_ratio: don't crop if detected border would remove more than this fraction from any side
        """
        if image.mode != 'RGBA':
            img = image.convert('RGBA')
        else:
            img = image

        width, height = img.size
        pixels = img.load()

        def is_bg(px):
            r, g, b, a = px
            # treat fully transparent as background too
            if a < 5:
                return True
            return r >= threshold and g >= threshold and b >= threshold

        # scan borders inwards to find first non-background pixel rows/cols
        top = 0
        while top < height and all(is_bg(pixels[x, top]) for x in range(width)):
            top += 1
        bottom = height - 1
        while bottom >= 0 and all(is_bg(pixels[x, bottom]) for x in range(width)):
            bottom -= 1
        left = 0
        while left < width and all(is_bg(pixels[left, y]) for y in range(height)):
            left += 1
        right = width - 1
        while right >= 0 and all(is_bg(pixels[right, y]) for y in range(height)):
            right -= 1

        # If no crop detected, return original
        if left == 0 and top == 0 and right == width - 1 and bottom == height - 1:
            return image

        # Validate crop is not excessive
        if (
            left / width > max_border_ratio or
            top / height > max_border_ratio or
            (width - 1 - right) / width > max_border_ratio or
            (height - 1 - bottom) / height > max_border_ratio or
            right <= left or bottom <= top
        ):
            return image

        cropped = img.crop((left, top, right + 1, bottom + 1))
        return cropped
    
    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from Django storage."""
        try:
            # Try to get the file from Django storage
            with default_storage.open(image_path, 'rb') as f:
                # Read the file content into memory to avoid file handle issues
                image_data = f.read()
                from io import BytesIO
                return Image.open(BytesIO(image_data))
        except Exception as e:
            logger.error(f"Failed to load image from storage: {str(e)}")
            # Fallback: try direct file system access
            try:
                full_path = default_storage.path(image_path)
                return Image.open(full_path)
            except Exception as fs_error:
                logger.error(f"Failed to load image from file system: {str(fs_error)}")
                return None
    
    def _add_logo_overlay(self, poster_image: Image.Image, company_profile) -> Tuple[Image.Image, Optional[Dict[str, int]]]:
        """Add company logo overlay to poster and return metadata."""
        try:
            # Check if logo exists and is valid
            if not company_profile.logo or not company_profile.logo.name:
                logger.warning("No logo found for company profile")
                return poster_image, None
            
            # Check if logo file exists
            if not os.path.exists(company_profile.logo.path):
                logger.warning(f"Logo file not found at path: {company_profile.logo.path}")
                return poster_image, None
            
            # Load company logo
            logo_image = self._load_image(company_profile.logo.path)
            if not logo_image:
                logger.warning("Failed to load logo image")
                return poster_image, None
            
            # Resize logo by width only, preserving aspect ratio
            target_width = self.logo_size[0]
            try:
                original_width, original_height = logo_image.size
                if original_width <= 0 or original_height <= 0:
                    logger.warning("Invalid logo dimensions; skipping resize")
                else:
                    scale = target_width / float(original_width)
                    target_height = max(1, int(original_height * scale))
                    logo_image = logo_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
            except Exception as e:
                logger.warning(f"Logo resize failed, using original size: {str(e)}")
            
            # Convert logo to RGBA if not already
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')

            # No stroke applied to logo
            
            # Calculate logo position based on preference
            position = self._calculate_logo_position(
                poster_image.size, 
                logo_image.size, 
                company_profile.preferred_logo_position
            )
            
            # Create a transparent overlay for the logo
            logo_overlay = Image.new('RGBA', poster_image.size, (0, 0, 0, 0))
            # Paste the logo directly without stroke
            logo_overlay.paste(logo_image, position, logo_image)
            
            # Composite the logo onto the poster
            poster_image = Image.alpha_composite(poster_image, logo_overlay)
            
            logger.info(f"Logo overlay added at position {position}")
            meta = {
                "x": int(position[0]),
                "y": int(position[1]),
                "width": int(logo_image.size[0]),
                "height": int(logo_image.size[1])
            }
            return poster_image, meta
            
        except Exception as e:
            logger.error(f"Error adding logo overlay: {str(e)}")
            return poster_image, None
    
    def _add_contact_overlay(self, 
                           poster_image: Image.Image, 
                           contact_info: Dict[str, str],
                           company_profile) -> Tuple[Image.Image, Optional[Dict[str, Any]]]:
        """Add contact information with proper spacing."""
        try:
            # Prepare contact items
            contact_items = self._prepare_contact_items(contact_info)
            
            if not contact_items:
                logger.warning("No contact information to display")
                return poster_image, None

            # Create drawing context
            draw = ImageDraw.Draw(poster_image)

            # Choose smaller font to fit within frame
            desired_size = max(18, int(min(poster_image.size) * 0.025))
            font = None
            font_paths = [
                # Prefer bold fonts
                "C:/Windows/Fonts/segoeuib.ttf",  # Segoe UI Bold
                "C:/Windows/Fonts/arialbd.ttf",   # Arial Bold
                "C:/Windows/Fonts/calibrib.ttf",  # Calibri Bold
                "C:/Windows/Fonts/Poppins-Bold.ttf",
                # Regular fallbacks
                "C:/Windows/Fonts/segui.ttf",     # Segoe UI Regular
                # macOS fonts
                "/System/Library/Fonts/Apple Color Emoji.ttc",
                "/System/Library/Fonts/Helvetica.ttf",
                "/System/Library/Fonts/Arial.ttf",
                # Linux fonts
                "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
                # Fallback fonts
                "C:/Windows/Fonts/arial.ttf",     # Arial Regular
                "C:/Windows/Fonts/calibri.ttf",   # Calibri Regular
            ]
            for fp in font_paths:
                try:
                    if os.path.exists(fp):
                        font = ImageFont.truetype(fp, desired_size)
                        logger.info(f"Using font: {fp}")
                        break
                except Exception as e:
                    logger.debug(f"Failed to load font {fp}: {e}")
                    continue
            if not font:
                font = ImageFont.load_default()
                logger.warning("Using default font - emoji support may be limited")

            # Calculate total width needed for all contact items (text only)
            total_width = 0
            item_widths = []
            spacing = 25  # Increased from 15 to add extra 10px
            
            for item in contact_items:
                # Calculate text width
                text = f"{item['value']}"
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                item_width = text_width
                item_widths.append(item_width)
                total_width += item_width + spacing

            # Center horizontally and place near bottom
            start_x = max(10, (poster_image.width - total_width) // 2)
            y_margin = max(20, int(poster_image.height * 0.04))
            y = poster_image.height - y_margin - desired_size

            current_x = start_x
            text_color = (255, 255, 255, 255)

            # Draw each contact item as text only
            for i, item in enumerate(contact_items):
                # Draw text without icons
                text_x = current_x
                text_y = y
                draw.text((text_x, text_y), item['value'], font=font, fill=text_color)
                
                # Move to next item
                current_x += item_widths[i] + spacing

            logger.info("Contact information rendered successfully")
            meta = {
                "x": int(start_x),
                "y": int(y),
                "width": int(total_width),
                "height": int(desired_size),
                "font_size": int(getattr(font, "size", desired_size)),
                "text": "Contact items"
            }
            return poster_image, meta

        except Exception as e:
            logger.error(f"Error adding contact overlay: {str(e)}")
            return poster_image, None
    
    def _calculate_logo_position(self, 
                               poster_size: Tuple[int, int], 
                               logo_size: Tuple[int, int],
                               position_preference: str) -> Tuple[int, int]:
        """Calculate logo position based on preference."""
        poster_width, poster_height = poster_size
        logo_width, logo_height = logo_size
        
        positions = {
            'top_right': (poster_width - logo_width - self.margin, self.margin),
            'bottom_right': (poster_width - logo_width - self.margin, poster_height - logo_height - self.margin),
            'top_left': (self.margin, self.margin),
            'bottom_left': (self.margin, poster_height - logo_height - self.margin)
        }
        
        return positions.get(position_preference, positions['top_right'])
    
    def _calculate_contact_position(self, poster_size: Tuple[int, int]) -> Tuple[int, int]:
        """Calculate contact information position (bottom-left)."""
        return (self.margin, poster_size[1] - 120)  # 120px from bottom
    
    def _analyze_poster_colors(self, poster_image: Image.Image) -> Dict[str, Any]:
        """Analyze poster colors to determine context-aware styling."""
        try:
            # Resize image for faster analysis
            small_image = poster_image.resize((100, 100), Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed
            if small_image.mode != 'RGB':
                small_image = small_image.convert('RGB')
            
            # Get color palette
            colors = small_image.getcolors(maxcolors=256*256*256)
            if not colors:
                return {'dominant': (0, 0, 0), 'brightness': 0.5, 'theme': 'neutral'}
            
            # Sort by frequency and get dominant color
            colors.sort(key=lambda x: x[0], reverse=True)
            dominant_color = colors[0][1]
            
            # Calculate brightness
            brightness = sum(dominant_color) / (3 * 255)
            
            # Determine theme based on colors
            theme = self._determine_color_theme(dominant_color, brightness)
            
            return {
                'dominant': dominant_color,
                'brightness': brightness,
                'theme': theme,
                'is_dark': brightness < 0.4,
                'is_warm': self._is_warm_color(dominant_color)
            }
            
        except Exception as e:
            logger.warning(f"Color analysis failed: {str(e)}")
            return {'dominant': (0, 0, 0), 'brightness': 0.5, 'theme': 'neutral'}
    
    def _determine_color_theme(self, color: Tuple[int, int, int], brightness: float) -> str:
        """Determine color theme based on dominant color."""
        r, g, b = color
        
        # Check for specific color themes
        if r > g + 50 and r > b + 50:  # Red dominant
            return 'warm' if brightness > 0.6 else 'dramatic'
        elif g > r + 50 and g > b + 50:  # Green dominant
            return 'natural' if brightness > 0.6 else 'earthy'
        elif b > r + 50 and b > g + 50:  # Blue dominant
            return 'cool' if brightness > 0.6 else 'professional'
        elif abs(r - g) < 30 and abs(g - b) < 30:  # Neutral colors
            return 'neutral'
        else:
            return 'vibrant' if brightness > 0.6 else 'muted'
    
    def _is_warm_color(self, color: Tuple[int, int, int]) -> bool:
        """Check if color is warm (reds, oranges, yellows)."""
        r, g, b = color
        return r > g and r > b
    
    def _get_context_aware_styling(self, color_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get styling configuration based on poster color analysis."""
        theme = color_analysis.get('theme', 'neutral')
        is_dark = color_analysis.get('is_dark', False)
        is_warm = color_analysis.get('is_warm', False)
        
        # Define styling presets based on theme
        styling_presets = {
            'warm': {
                'background': (139, 69, 19, 200) if is_dark else (255, 248, 220, 200),
                'text_color': (255, 255, 255) if is_dark else (139, 69, 19),
                'accent_color': (255, 140, 0),
                'border_color': (255, 165, 0),
                'icon_style': 'warm'
            },
            'cool': {
                'background': (25, 25, 112, 200) if is_dark else (240, 248, 255, 200),
                'text_color': (255, 255, 255) if is_dark else (25, 25, 112),
                'accent_color': (0, 191, 255),
                'border_color': (30, 144, 255),
                'icon_style': 'cool'
            },
            'natural': {
                'background': (34, 139, 34, 200) if is_dark else (240, 255, 240, 200),
                'text_color': (255, 255, 255) if is_dark else (34, 139, 34),
                'accent_color': (50, 205, 50),
                'border_color': (0, 128, 0),
                'icon_style': 'natural'
            },
            'professional': {
                'background': (47, 79, 79, 200) if is_dark else (248, 249, 250, 200),
                'text_color': (255, 255, 255) if is_dark else (47, 79, 79),
                'accent_color': (70, 130, 180),
                'border_color': (100, 149, 237),
                'icon_style': 'professional'
            },
            'vibrant': {
                'background': (75, 0, 130, 200) if is_dark else (255, 240, 245, 200),
                'text_color': (255, 255, 255) if is_dark else (75, 0, 130),
                'accent_color': (255, 20, 147),
                'border_color': (186, 85, 211),
                'icon_style': 'vibrant'
            }
        }
        
        # Default to neutral if theme not found
        return styling_presets.get(theme, styling_presets['professional'])
    
    def _load_enhanced_fonts(self) -> Tuple[ImageFont.ImageFont, ImageFont.ImageFont]:
        """Load enhanced fonts for better typography."""
        title_size = 24
        body_size = 18
        
        # Try to load better fonts
        font_paths = [
            # Windows fonts
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/segoeui.ttf",
            # macOS fonts
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Helvetica.ttf",
            "/System/Library/Fonts/San Francisco.ttf",
            # Linux fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
        ]
        
        title_font = None
        body_font = None
        
        for font_path in font_paths:
            try:
                if os.path.exists(font_path):
                    title_font = ImageFont.truetype(font_path, title_size)
                    body_font = ImageFont.truetype(font_path, body_size)
                    break
            except:
                continue
        
        # Fallback to default fonts
        if not title_font:
            title_font = ImageFont.load_default()
        if not body_font:
            body_font = ImageFont.load_default()
        
        return title_font, body_font
    
    def _prepare_contact_items(self, contact_info: Dict[str, str]) -> List[Dict[str, Any]]:
        """Prepare contact items with text formatting only."""
        items = []
        
        # WhatsApp contact
        if 'whatsapp' in contact_info and contact_info['whatsapp']:
            items.append({
                'type': 'whatsapp',
                'label': 'WhatsApp',
                'value': contact_info['whatsapp']
            })
        
        # Facebook contact
        if 'facebook' in contact_info and contact_info['facebook']:
            items.append({
                'type': 'facebook',
                'label': 'Facebook',
                'value': contact_info['facebook']
            })
        
        # Email contact
        if 'email' in contact_info and contact_info['email']:
            items.append({
                'type': 'email',
                'label': 'Email',
                'value': contact_info['email']
            })
        
        # Phone contact
        if 'phone' in contact_info and contact_info['phone']:
            items.append({
                'type': 'phone',
                'label': 'Phone',
                'value': contact_info['phone']
            })
        
        # Website contact
        if 'website' in contact_info and contact_info['website']:
            items.append({
                'type': 'website',
                'label': 'Website',
                'value': contact_info['website']
            })
        
        return items
    
    def _calculate_enhanced_overlay_dimensions(self, 
                                             poster_size: Tuple[int, int], 
                                             contact_items: List[Dict[str, Any]],
                                             title_font: ImageFont.ImageFont,
                                             body_font: ImageFont.ImageFont) -> Dict[str, Any]:
        """Calculate enhanced overlay dimensions."""
        poster_width, poster_height = poster_size
        
        # Calculate text dimensions
        title_height = title_font.getbbox("Contact Us")[3] - title_font.getbbox("Contact Us")[1]
        item_height = body_font.getbbox("Sample Text")[3] - body_font.getbbox("Sample Text")[1]
        
        # Calculate total height
        padding = 40
        title_spacing = 20
        item_spacing = 25  # Increased from 15 to add extra 10px
        total_height = padding + title_height + title_spacing + (len(contact_items) * (item_height + item_spacing)) + padding
        
        return {
            'width': poster_width,
            'height': total_height,
            'padding': padding,
            'title_height': title_height,
            'item_height': item_height,
            'title_spacing': title_spacing,
            'item_spacing': item_spacing
        }
    
    def _create_enhanced_overlay(self, 
                                overlay_config: Dict[str, Any], 
                                styling_config: Dict[str, Any]) -> Image.Image:
        """Create enhanced overlay with gradient background."""
        width = overlay_config['width']
        height = overlay_config['height']
        
        # Create base overlay
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Create gradient background
        bg_color = styling_config['background']
        
        # Create rounded rectangle background
        corner_radius = 20
        self._draw_rounded_rectangle(
            draw, (0, 0, width, height), 
            bg_color, corner_radius
        )
        
        # Add subtle border
        border_color = styling_config['border_color']
        border_width = 2
        self._draw_rounded_rectangle(
            draw, (border_width, border_width, width - border_width, height - border_width),
            border_color + (255,), corner_radius - border_width, outline=True
        )
        
        return overlay
    
    def _draw_rounded_rectangle(self, 
                               draw: ImageDraw.Draw, 
                               bounds: Tuple[int, int, int, int], 
                               color: Tuple[int, int, int, int], 
                               radius: int, 
                               outline: bool = False):
        """Draw a rounded rectangle."""
        x1, y1, x2, y2 = bounds
        
        if outline:
            # Draw outline
            draw.rectangle([x1, y1, x2, y2], fill=None, outline=color[:3], width=2)
        else:
            # Draw filled rounded rectangle
            draw.rectangle([x1, y1, x2, y2], fill=color)
    
    def _draw_enhanced_contact_info(self, 
                                  draw: ImageDraw.Draw,
                                  poster_image: Image.Image,
                                  contact_items: List[Dict[str, Any]],
                                  overlay_y: int,
                                  overlay_config: Dict[str, Any],
                                  title_font: ImageFont.ImageFont,
                                  body_font: ImageFont.ImageFont,
                                  styling_config: Dict[str, Any]):
        """Draw enhanced contact information with proper styling."""
        x_offset = 30
        y_offset = overlay_y + overlay_config['padding']
        
        # Draw title
        title_text = "Contact Us"
        title_color = styling_config['text_color']
        draw.text((x_offset, y_offset), title_text, font=title_font, fill=title_color)
        y_offset += overlay_config['title_height'] + overlay_config['title_spacing']
        
        # Draw contact items
        for item in contact_items:
            # Draw label and value (text only)
            text_x = x_offset
            text_y = y_offset
            
            # Label
            label_text = f"{item['label']}:"
            draw.text((text_x, text_y), label_text, font=body_font, fill=styling_config['text_color'])
            
            # Value
            value_text = item['value']
            value_x = text_x + body_font.getbbox(label_text)[2] + 10
            draw.text((value_x, text_y), value_text, font=body_font, fill=styling_config['accent_color'])
            
            y_offset += overlay_config['item_height'] + overlay_config['item_spacing']
    
    def _save_final_image(self, image: Image.Image, output_filename: Optional[str] = None) -> Optional[str]:
        """Save the final image with brand overlay."""
        try:
            # Generate filename if not provided
            if not output_filename:
                timestamp = int(time.time())
                output_filename = f"branded_poster_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not output_filename.endswith('.png'):
                output_filename += '.png'
            
            output_path = f"branded_posters/{output_filename}"
            
            # Convert back to RGB for saving (remove alpha channel)
            if image.mode == 'RGBA':
                # Create a white background
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # Use alpha channel as mask
                image = background
            
            # Save to Django storage
            image_bytes = BytesIO()
            image.save(image_bytes, format='PNG', quality=95)
            image_bytes.seek(0)
            
            saved_path = default_storage.save(output_path, ContentFile(image_bytes.getvalue()))
            return saved_path
            
        except Exception as e:
            logger.error(f"Error saving final image: {str(e)}")
            return None
    
    def create_branded_poster(self, 
                            poster_path: str, 
                            company_profile,
                            output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a branded poster with company logo and contact information.
        
        Args:
            poster_path: Path to the AI-generated poster
            company_profile: CompanyProfile instance
            output_filename: Optional custom filename
            
        Returns:
            Dict containing status and final image details
        """
        try:
            if not company_profile or not company_profile.has_complete_profile:
                logger.warning("Company profile incomplete, skipping brand overlay")
                return {
                    "status": "warning",
                    "message": "Company profile incomplete, returning original poster",
                    "image_path": poster_path,
                    "image_url": default_storage.url(poster_path),
                    "branding_applied": False
                }
            
            # Add brand overlay
            result = self.add_brand_overlay(poster_path, company_profile, output_filename)
            
            if result.get('status') == 'success':
                logger.info("Branded poster created successfully")
                return result
            else:
                # Return original poster if branding fails
                logger.warning(f"Brand overlay failed: {result.get('message')}, returning original")
                return {
                    "status": "warning",
                    "message": f"Brand overlay failed: {result.get('message')}",
                    "image_path": poster_path,
                    "image_url": default_storage.url(poster_path),
                    "branding_applied": False
                }
                
        except Exception as e:
            logger.error(f"Error creating branded poster: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "image_path": poster_path,
                "image_url": default_storage.url(poster_path),
                "branding_applied": False
            }

