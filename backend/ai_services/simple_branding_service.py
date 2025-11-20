"""
Simple Branding Service
A more direct approach to include branding in AI-generated posters.
"""

import os
import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()

class SimpleBrandingService:
    """
    Simple service for adding branding to AI prompts.
    """
    
    def enhance_prompt_with_branding(self, prompt: str, user=None) -> str:
        """
        Enhance the prompt with company branding information.
        
        Args:
            prompt: Original user prompt
            user: User object with company profile
            
        Returns:
            Enhanced prompt with branding information
        """
        if not user:
            return prompt
            
        try:
            from users.models import CompanyProfile
            company_profile = getattr(user, 'company_profile', None)
            
            if not company_profile or not company_profile.has_complete_profile:
                logger.info("No complete company profile found - using original prompt")
                return prompt
            
            # Get company branding information
            company_name = company_profile.company_name or ""
            contact_info = company_profile.get_contact_info()
            
            # Build contact details text with proper formatting
            contact_details = []
            if contact_info.get('whatsapp'):
                contact_details.append(f"📱 WhatsApp: {contact_info['whatsapp']}")
            if contact_info.get('email'):
                contact_details.append(f"✉️ Email: {contact_info['email']}")
            
            # Join with proper line breaks for better formatting
            contact_text = "\n".join(contact_details) if contact_details else ""
            
            # Create a comprehensive branding prompt
            branding_prompt = f"""
Create a professional textile poster with the following requirements:

DESIGN BRIEF: {prompt}

BRANDING REQUIREMENTS:
- Company Name: {company_name}
- Contact Information: {contact_text}
- Include company logo in the design (position it appropriately)
- Make the poster look professional and branded
- Ensure all text is clearly readable
- Use high-quality design elements

The poster should be a complete, professional marketing material that includes all the branding elements naturally integrated into the design.
"""
            
            logger.info(f"Enhanced prompt with comprehensive branding: {branding_prompt[:200]}...")
            return branding_prompt.strip()
            
        except Exception as e:
            logger.error(f"Error enhancing prompt with branding: {str(e)}")
            return prompt
    
    def create_branded_prompt(self, prompt: str, user=None) -> Dict[str, Any]:
        """
        Create a branded prompt with all company information.
        
        Args:
            prompt: Original user prompt
            user: User object with company profile
            
        Returns:
            Dict containing enhanced prompt and branding status
        """
        if not user:
            return {
                "enhanced_prompt": prompt,
                "has_branding": False,
                "company_name": None,
                "contact_info": None
            }
            
        try:
            from users.models import CompanyProfile
            company_profile = getattr(user, 'company_profile', None)
            
            if not company_profile or not company_profile.has_complete_profile:
                return {
                    "enhanced_prompt": prompt,
                    "has_branding": False,
                    "company_name": None,
                    "contact_info": None
                }
            
            # Get company information
            company_name = company_profile.company_name
            contact_info = company_profile.get_contact_info()
            has_logo = bool(company_profile.logo)
            
            # Create enhanced prompt
            enhanced_prompt = self.enhance_prompt_with_branding(prompt, user)
            
            return {
                "enhanced_prompt": enhanced_prompt,
                "has_branding": True,
                "company_name": company_name,
                "contact_info": contact_info,
                "has_logo": has_logo,
                "logo_position": company_profile.preferred_logo_position
            }
            
        except Exception as e:
            logger.error(f"Error creating branded prompt: {str(e)}")
            return {
                "enhanced_prompt": prompt,
                "has_branding": False,
                "company_name": None,
                "contact_info": None
            }

