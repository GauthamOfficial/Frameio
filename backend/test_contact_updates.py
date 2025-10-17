#!/usr/bin/env python3
"""
Test script to verify the updated contact information with Facebook, icons, and Poppins font
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

def test_contact_updates():
    """Test the updated contact information display"""
    try:
        logger.info("=== Testing Updated Contact Information ===")
        
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
                company_profile = test_user.company_profile
                
                # Add Facebook username for testing
                if not company_profile.facebook_username:
                    company_profile.facebook_username = "madhugai.textiles"
                    company_profile.save()
                    logger.info("Added Facebook username for testing")
                
                logger.info(f"Using test user: {test_user.username}")
                logger.info(f"Company: {company_profile.company_name}")
                logger.info(f"Has logo: {bool(company_profile.logo)}")
                logger.info(f"Contact info: {company_profile.get_contact_info()}")
            else:
                logger.warning("No users with complete company profiles found")
                logger.info("Testing without branding...")
        except Exception as e:
            logger.error(f"Error finding test user: {e}")
        
        # Test prompt for contact updates
        test_prompt = "Create a beautiful textile poster for a premium silk saree collection with elegant patterns"
        
        logger.info(f"\n--- Testing Updated Contact Information ---")
        logger.info(f"Prompt: {test_prompt}")
        logger.info("Expected changes:")
        logger.info("- Contact details now include WhatsApp, Facebook, and Email")
        logger.info("- Icons: 📱 for WhatsApp, 📘 for Facebook, ✉️ for Email")
        logger.info("- Font: Poppins (with fallbacks)")
        logger.info("- Font size: Decreased to 22px for better fit")
        logger.info("- Single line display with proper spacing")
        
        try:
            # Generate poster with updated contact information
            result = poster_service.generate_from_prompt(
                prompt=test_prompt,
                aspect_ratio="1:1",
                user=test_user
            )
            
            if result.get('status') == 'success':
                logger.info("SUCCESS: Poster generated with updated contact information!")
                logger.info(f"Image path: {result.get('image_path')}")
                logger.info(f"Image URL: {result.get('image_url')}")
                logger.info(f"Branding applied: {result.get('branding_applied', False)}")
                logger.info(f"Logo added: {result.get('logo_added', False)}")
                logger.info(f"Contact info added: {result.get('contact_info_added', False)}")
                
                # Check branding metadata for contact info
                branding_metadata = result.get('branding_metadata', {})
                if branding_metadata:
                    contact_meta = branding_metadata.get('contact', {})
                    if contact_meta:
                        logger.info(f"Contact text: {contact_meta.get('text')}")
                        logger.info(f"Contact font size: {contact_meta.get('font_size')}")
                        logger.info(f"Contact position: ({contact_meta.get('x')}, {contact_meta.get('y')})")
                        
                        # Check if all three contact types are included
                        contact_text = contact_meta.get('text', '')
                        if '📱' in contact_text and '📘' in contact_text and '✉️' in contact_text:
                            logger.info("SUCCESS: All three contact types with icons are included!")
                        else:
                            logger.warning("WARNING: Not all contact types are included")
                
                logger.info("Updated contact information should be visible in the generated poster!")
            else:
                logger.error(f"FAILED: Poster generation failed: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"ERROR: Error testing contact updates: {str(e)}")
            return False
        
        logger.info("\n=== Contact Updates Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_contact_info_method():
    """Test the updated get_contact_info method"""
    try:
        logger.info("\n=== Testing Contact Info Method ===")
        
        # Get a user with company profile
        User = get_user_model()
        test_user = None
        
        try:
            company_profiles = CompanyProfile.objects.filter(
                logo__isnull=False,
                company_name__isnull=False
            ).exclude(company_name='').exclude(logo='')
            
            if company_profiles.exists():
                test_user = company_profiles.first().user
                company_profile = test_user.company_profile
                
                # Add Facebook username if not present
                if not company_profile.facebook_username:
                    company_profile.facebook_username = "madhugai.textiles"
                    company_profile.save()
                
                # Test get_contact_info method
                contact_info = company_profile.get_contact_info()
                logger.info(f"Contact info: {contact_info}")
                
                # Check if all expected fields are present
                expected_fields = ['whatsapp', 'email', 'facebook']
                for field in expected_fields:
                    if field in contact_info:
                        logger.info(f"SUCCESS: {field} is present: {contact_info[field]}")
                    else:
                        logger.warning(f"WARNING: {field} is missing")
                
                return True
            else:
                logger.warning("No test user with company profile found")
                return False
        except Exception as e:
            logger.error(f"Error testing contact info method: {e}")
            return False
        
    except Exception as e:
        logger.error(f"ERROR: Error testing contact info method: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Updated Contact Information")
    print("=" * 50)
    
    # Test contact info method
    test_contact_info_method()
    
    # Test actual poster generation with updated contact information
    test_contact_updates()
    
    print("\nContact updates test completed!")
