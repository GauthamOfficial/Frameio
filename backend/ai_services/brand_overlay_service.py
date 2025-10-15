"""
Brand Overlay Service for AI-Generated Posters
Handles adding company branding (logo and contact info) to AI-generated poster images.
"""
import os
import time
import logging
from typing import Dict, Any, Optional, Tuple
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)


class BrandOverlayService:
    """
    Service for adding brand overlays to AI-generated poster images.
    """
    
    def __init__(self):
        """Initialize the brand overlay service."""
        self.default_font_size = 24
        self.logo_size = (150, 150)
        self.contact_font_size = 20
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
            if company_profile.logo:
                poster_image = self._add_logo_overlay(poster_image, company_profile)
            
            # Add contact information overlay
            contact_info = company_profile.get_contact_info()
            if contact_info:
                poster_image = self._add_contact_overlay(poster_image, contact_info, company_profile)
            
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
                    "contact_info_added": bool(contact_info)
                }
            else:
                return {"status": "error", "message": "Failed to save final image"}
                
        except Exception as e:
            logger.error(f"Error adding brand overlay: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def _load_image(self, image_path: str) -> Optional[Image.Image]:
        """Load image from Django storage."""
        try:
            # Try to get the file from Django storage
            with default_storage.open(image_path, 'rb') as f:
                return Image.open(f)
        except Exception as e:
            logger.error(f"Failed to load image from storage: {str(e)}")
            # Fallback: try direct file system access
            try:
                full_path = default_storage.path(image_path)
                return Image.open(full_path)
            except Exception as fs_error:
                logger.error(f"Failed to load image from file system: {str(fs_error)}")
                return None
    
    def _add_logo_overlay(self, poster_image: Image.Image, company_profile) -> Image.Image:
        """Add company logo overlay to poster."""
        try:
            # Load company logo
            logo_image = self._load_image(company_profile.logo.path)
            if not logo_image:
                return poster_image
            
            # Resize logo to appropriate size
            logo_image = logo_image.resize(self.logo_size, Image.Resampling.LANCZOS)
            
            # Convert logo to RGBA if not already
            if logo_image.mode != 'RGBA':
                logo_image = logo_image.convert('RGBA')
            
            # Calculate logo position based on preference
            position = self._calculate_logo_position(
                poster_image.size, 
                self.logo_size, 
                company_profile.preferred_logo_position
            )
            
            # Create a transparent overlay for the logo
            logo_overlay = Image.new('RGBA', poster_image.size, (0, 0, 0, 0))
            logo_overlay.paste(logo_image, position, logo_image)
            
            # Composite the logo onto the poster
            poster_image = Image.alpha_composite(poster_image, logo_overlay)
            
            logger.info(f"Logo overlay added at position {position}")
            return poster_image
            
        except Exception as e:
            logger.error(f"Error adding logo overlay: {str(e)}")
            return poster_image
    
    def _add_contact_overlay(self, 
                           poster_image: Image.Image, 
                           contact_info: Dict[str, str],
                           company_profile) -> Image.Image:
        """Add contact information overlay to poster."""
        try:
            # Create a drawing context
            draw = ImageDraw.Draw(poster_image)
            
            # Try to load a font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", self.contact_font_size)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", self.contact_font_size)
                except:
                    font = ImageFont.load_default()
            
            # Calculate contact info position (bottom-left corner)
            contact_position = self._calculate_contact_position(poster_image.size)
            
            # Add contact information with icons
            y_offset = contact_position[1]
            line_height = self.contact_font_size + 10
            
            # WhatsApp
            if 'whatsapp' in contact_info:
                whatsapp_text = f"📱 {contact_info['whatsapp']}"
                draw.text((contact_position[0], y_offset), whatsapp_text, font=font, fill="white")
                y_offset += line_height
            
            # Email
            if 'email' in contact_info:
                email_text = f"✉️ {contact_info['email']}"
                draw.text((contact_position[0], y_offset), email_text, font=font, fill="white")
                y_offset += line_height
            
            # Facebook
            if 'facebook' in contact_info:
                facebook_text = f"📘 {contact_info['facebook']}"
                draw.text((contact_position[0], y_offset), facebook_text, font=font, fill="white")
                y_offset += line_height
            
            # Add company name if available
            if company_profile.company_name:
                company_text = f"🏢 {company_profile.company_name}"
                draw.text((contact_position[0], y_offset), company_text, font=font, fill="white")
            
            logger.info(f"Contact overlay added at position {contact_position}")
            return poster_image
            
        except Exception as e:
            logger.error(f"Error adding contact overlay: {str(e)}")
            return poster_image
    
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
