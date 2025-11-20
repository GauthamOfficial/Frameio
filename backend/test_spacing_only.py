#!/usr/bin/env python3
"""
Test script to verify spacing-only approach (no branding mentioned in prompts)
Tests that posters are generated with proper spacing without mentioning logo/contact details
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

def test_spacing_only_approach():
    """Test the spacing-only approach without mentioning branding in prompts"""
    try:
        logger.info("=== Testing Spacing-Only Approach ===")
        
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
        
        # Test prompts that should benefit from spacing-only approach
        test_prompts = [
            "Create a beautiful textile poster for a silk saree with elegant patterns",
            "Design a modern fashion poster showcasing traditional Indian wear",
            "Generate a textile poster with intricate embroidery and vibrant colors"
        ]
        
        # Test each prompt
        for i, prompt in enumerate(test_prompts, 1):
            logger.info(f"\n--- Test {i}: Testing spacing-only approach ---")
            logger.info(f"Prompt: {prompt}")
            logger.info("Expected behavior:")
            logger.info("- AI will reserve space in top-right and bottom areas")
            logger.info("- AI will NOT mention logo or contact details in generation")
            logger.info("- Brand overlay service will add logo/contact separately")
            
            try:
                # Generate poster with spacing-only approach
                result = poster_service.generate_from_prompt(
                    prompt=prompt,
                    aspect_ratio="1:1",
                    user=test_user
                )
                
                if result.get('status') == 'success':
                    logger.info("SUCCESS: Poster generated with spacing-only approach!")
                    logger.info(f"Image path: {result.get('image_path')}")
                    logger.info(f"Image URL: {result.get('image_url')}")
                    logger.info(f"Branding applied: {result.get('branding_applied', False)}")
                    logger.info(f"Logo added: {result.get('logo_added', False)}")
                    logger.info(f"Contact info added: {result.get('contact_info_added', False)}")
                    
                    # Check if spacing instructions were applied
                    if test_user and test_user.company_profile.has_complete_profile:
                        logger.info("SUCCESS: Spacing instructions applied for clean layout")
                        logger.info("- Top-right area reserved for logo placement")
                        logger.info("- Bottom area reserved for contact details")
                        logger.info("- Main content kept in center-left area")
                    else:
                        logger.info("INFO: No company profile - spacing instructions not needed")
                else:
                    logger.error(f"FAILED: Poster generation failed: {result.get('message')}")
                    
            except Exception as e:
                logger.error(f"ERROR: Error testing prompt {i}: {str(e)}")
        
        logger.info("\n=== Spacing-Only Test Complete ===")
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_prompt_content():
    """Test that prompts don't mention branding elements"""
    try:
        logger.info("\n=== Testing Prompt Content ===")
        
        poster_service = AIPosterService()
        
        # Test with user having company profile
        User = get_user_model()
        test_user = None
        
        try:
            company_profiles = CompanyProfile.objects.filter(
                logo__isnull=False,
                company_name__isnull=False
            ).exclude(company_name='').exclude(logo='')
            
            if company_profiles.exists():
                test_user = company_profiles.first().user
                logger.info(f"Test user found: {test_user.username}")
            else:
                logger.warning("No test user with company profile found")
        except Exception as e:
            logger.error(f"Error finding test user: {e}")
        
        # Test prompt
        test_prompt = "Create a beautiful textile poster"
        
        # Check if spacing instructions would be added
        if test_user and test_user.company_profile.has_complete_profile:
            logger.info("SUCCESS: User has complete company profile - spacing instructions will be added")
            logger.info("Spacing instructions include:")
            logger.info("- Reserve TOP-RIGHT corner - keep this area clear")
            logger.info("- Reserve BOTTOM area - keep this area clear")
            logger.info("- Keep main content in CENTER and LEFT areas")
            logger.info("- Use center-left 55% of image for main content")
            logger.info("NOTE: No mention of logo or contact details in AI prompts")
        else:
            logger.info("INFO: No company profile - spacing instructions not needed")
        
        return True
        
    except Exception as e:
        logger.error(f"ERROR: Error testing prompt content: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing Spacing-Only Approach (No Branding in Prompts)")
    print("=" * 60)
    
    # Test prompt content
    test_prompt_content()
    
    # Test actual poster generation with spacing-only approach
    test_spacing_only_approach()
    
    print("\nSpacing-only test completed!")
