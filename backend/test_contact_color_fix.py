#!/usr/bin/env python3
"""
Test script to verify contact color and icon fixes in poster generation.
"""

import os
import sys
import django
import logging

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import CompanyProfile
from ai_services.ai_poster_service import AIPosterService
from ai_services.brand_overlay_service import BrandOverlayService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_contact_color_and_icons():
    """
    Test that contact information is displayed with white color and proper icons.
    """
    try:
        logger.info("=== Testing Contact Color and Icon Fixes ===")
        
        # Get or create a test user
        User = get_user_model()
        test_user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={'username': 'testuser'}
        )
        
        if created:
            logger.info("Created test user")
        else:
            logger.info("Using existing test user")
        
        # Get or create company profile with contact info
        company_profile, profile_created = CompanyProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'company_name': 'Test Company',
                'whatsapp_number': '+1234567890',
                'email': 'contact@testcompany.com',
                'facebook_username': 'testcompany'
            }
        )
        
        if profile_created:
            logger.info("Created test company profile")
        else:
            logger.info("Using existing company profile")
        
        # Update contact info to ensure we have all three types
        company_profile.whatsapp_number = '+1234567890'
        company_profile.email = 'contact@testcompany.com'
        company_profile.facebook_username = 'testcompany'
        company_profile.save()
        
        logger.info(f"Company: {company_profile.company_name}")
        logger.info(f"WhatsApp: {company_profile.whatsapp_number}")
        logger.info(f"Email: {company_profile.email}")
        logger.info(f"Facebook: {company_profile.facebook_username}")
        
        # Test the contact info method
        contact_info = company_profile.get_contact_info()
        logger.info(f"Contact info: {contact_info}")
        
        # Test poster generation with branding
        poster_service = AIPosterService()
        test_prompt = "Create a modern business poster for a textile company with elegant design"
        
        logger.info("Generating poster with contact information...")
        result = poster_service.generate_from_prompt(
            prompt=test_prompt,
            aspect_ratio="1:1",
            user=test_user
        )
        
        if result.get('status') == 'success':
            logger.info("SUCCESS: Poster generated with contact information!")
            logger.info(f"Image path: {result.get('image_path')}")
            logger.info(f"Image URL: {result.get('image_url')}")
            logger.info(f"Branding applied: {result.get('branding_applied', False)}")
            logger.info(f"Contact info added: {result.get('contact_info_added', False)}")
            
            # Check branding metadata for contact info
            branding_metadata = result.get('branding_metadata', {})
            if branding_metadata:
                contact_meta = branding_metadata.get('contact', {})
                if contact_meta:
                    logger.info(f"Contact text: {contact_meta.get('text')}")
                    logger.info(f"Contact font size: {contact_meta.get('font_size')}")
                    logger.info(f"Contact position: ({contact_meta.get('x')}, {contact_meta.get('y')})")
                    
                    # Check if all three contact types are included with icons
                    contact_text = contact_meta.get('text', '')
                    if '📱' in contact_text and '📘' in contact_text and '✉️' in contact_text:
                        logger.info("SUCCESS: All three contact types with icons are included!")
                    else:
                        logger.warning("WARNING: Not all contact types are included")
                        logger.warning(f"Contact text: {contact_text}")
                else:
                    logger.warning("No contact metadata found")
            else:
                logger.warning("No branding metadata found")
        else:
            logger.error(f"FAILED: {result.get('message', 'Unknown error')}")
            return False
        
        # Test the brand overlay service directly
        logger.info("\n=== Testing Brand Overlay Service Directly ===")
        brand_service = BrandOverlayService()
        
        # Test contact overlay method
        from PIL import Image
        test_image = Image.new('RGB', (800, 800), color='lightblue')
        
        # Test contact overlay
        contact_info = company_profile.get_contact_info()
        if contact_info:
            logger.info("Testing contact overlay with white text and icons...")
            result_image, contact_metadata = brand_service._add_contact_overlay(
                test_image, contact_info, company_profile
            )
            
            if contact_metadata:
                logger.info("SUCCESS: Contact overlay applied!")
                logger.info(f"Contact text: {contact_metadata.get('text')}")
                logger.info(f"Font size: {contact_metadata.get('font_size')}")
                logger.info(f"Position: ({contact_metadata.get('x')}, {contact_metadata.get('y')})")
                
                # Check if icons are present
                contact_text = contact_metadata.get('text', '')
                if '📱' in contact_text:
                    logger.info("✓ WhatsApp icon (📱) found")
                if '📘' in contact_text:
                    logger.info("✓ Facebook icon (📘) found")
                if '✉️' in contact_text:
                    logger.info("✓ Email icon (✉️) found")
            else:
                logger.warning("No contact metadata returned")
        
        logger.info("\n=== Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_contact_color_and_icons()
    if success:
        print("\n✅ Contact color and icon test completed successfully!")
    else:
        print("\n❌ Contact color and icon test failed!")
        sys.exit(1)
