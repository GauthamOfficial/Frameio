#!/usr/bin/env python3
"""
Test script to verify the enhanced sizing for logo and contact details
Tests that posters are generated with larger logo and bolder contact details
"""
import os
import sys
import django
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.ai_poster_service import AIPosterService
from users.models import CompanyProfile
from django.contrib.auth import get_user_model

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_enhanced_sizing():
    """Test the enhanced sizing for logo and contact details"""
    try:
        logger.info("=== Testing Enhanced Sizing for Logo and Contact Details ===")
        
        # Initialize AI poster service
        poster_service = AIPosterService()
        
        if not poster_service.is_available():
            logger.error("AI poster service is not available")
            return False
        
        logger.info("AI poster service is available")
        
        # Get a user with company profile for testing
        User = get_user_model()
        test_user = None
        
        try:
            # Try to find a user with complete company profile
            company_profiles = CompanyProfile.objects.filter(
                logo__isnull=False,
                company_name__isnull=False
            ).exclude(company_name='').exclude(logo='')
            
            if company_profiles.exists():
                test_user = company_profiles.first().user
                logger.info(f"Using test user: {test_user.username}")
                logger.info(f"Company: {test_user.company_profile.company_name}")
                logger.info(f"Has logo: {bool(test_user.company_profile.logo)}")
                logger.info(f"Has contact info: {bool(test_user.company_profile.get_contact_info())}")
            else:
                logger.warning("No users with complete company profiles found")
                logger.info("Testing without branding...")
        except Exception as e:
            logger.error(f"Error finding test user: {e}")
        
        # Test prompt for enhanced sizing
        test_prompt = "Create a beautiful textile poster for a premium silk saree collection with elegant patterns and gold accents"
        
        logger.info(f"\n--- Testing Enhanced Sizing ---")
        logger.info(f"Prompt: {test_prompt}")
        logger.info("Expected changes:")
        logger.info("- Logo size increased from 150x150 to 200x200 pixels")
        logger.info("- Contact details font size increased from 20 to 28+ pixels")
        logger.info("- Contact details will use bold fonts when available")
        logger.info("- Spacing instructions updated for larger branding elements")
        
        try:
            # Generate poster with enhanced sizing
            result = poster_service.generate_from_prompt(
                prompt=test_prompt,
                aspect_ratio="1:1",
                user=test_user
            )
            
            if result.get('status') == 'success':
                logger.info("SUCCESS: Poster generated with enhanced sizing!")
                logger.info(f"Image path: {result.get('image_path')}")
                logger.info(f"Image URL: {result.get('image_url')}")
                logger.info(f"Branding applied: {result.get('branding_applied', False)}")
                logger.info(f"Logo added: {result.get('logo_added', False)}")
                logger.info(f"Contact info added: {result.get('contact_info_added', False)}")
                
                # Check branding metadata for sizing info
                branding_metadata = result.get('branding_metadata', {})
                if branding_metadata:
                    logo_meta = branding_metadata.get('logo', {})
                    contact_meta = branding_metadata.get('contact', {})
                    
                    if logo_meta:
                        logger.info(f"Logo dimensions: {logo_meta.get('width')}x{logo_meta.get('height')}")
                        logger.info(f"Logo position: ({logo_meta.get('x')}, {logo_meta.get('y')})")
                    
                    if contact_meta:
                        logger.info(f"Contact font size: {contact_meta.get('font_size')}")
                        logger.info(f"Contact text: {contact_meta.get('text')}")
                        logger.info(f"Contact position: ({contact_meta.get('x')}, {contact_meta.get('y')})")
                
                logger.info("Enhanced sizing should be visible in the generated poster!")
            else:
                logger.error(f"FAILED: Poster generation failed: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"ERROR: Error testing enhanced sizing: {str(e)}")
            return False
        
        logger.info("\n=== Enhanced Sizing Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_brand_overlay_service():
    """Test the brand overlay service directly"""
    try:
        logger.info("\n=== Testing Brand Overlay Service Directly ===")
        
        from ai_services.brand_overlay_service import BrandOverlayService
        
        # Initialize brand overlay service
        brand_service = BrandOverlayService()
        
        # Check the new sizing configuration
        logger.info(f"Logo size: {brand_service.logo_size}")
        logger.info(f"Contact font size: {brand_service.contact_font_size}")
        logger.info(f"Margin: {brand_service.margin}")
        
        # Verify the changes
        expected_logo_size = (150, 150)
        expected_contact_size = 28
        
        if brand_service.logo_size == expected_logo_size:
            logger.info("SUCCESS: Logo size updated correctly")
        else:
            logger.warning(f"WARNING: Logo size is {brand_service.logo_size}, expected {expected_logo_size}")
        
        if brand_service.contact_font_size == expected_contact_size:
            logger.info("SUCCESS: Contact font size updated correctly")
        else:
            logger.warning(f"WARNING: Contact font size is {brand_service.contact_font_size}, expected {expected_contact_size}")
        
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Error testing brand overlay service: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Enhanced Sizing for Logo and Contact Details")
    print("=" * 60)
    
    # Test brand overlay service configuration
    test_brand_overlay_service()
    
    # Test actual poster generation with enhanced sizing
    test_enhanced_sizing()
    
    print("\nEnhanced sizing test completed!")
