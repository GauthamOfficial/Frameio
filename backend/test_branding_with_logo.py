#!/usr/bin/env python
"""
Test script to verify branding with actual logo file
"""
import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from users.models import User, CompanyProfile
from ai_services.ai_poster_service import AIPosterService
from ai_services.brand_overlay_service import BrandOverlayService
from django.core.files import File
from PIL import Image
import tempfile
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_test_logo():
    """Create a test logo file"""
    # Create a simple logo image
    logo_image = Image.new('RGB', (200, 200), color='blue')
    
    # Add some text to make it look like a logo
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(logo_image)
    
    # Try to use a default font
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # Draw company name
    draw.text((50, 80), "TEST", fill='white', font=font)
    draw.text((50, 100), "LOGO", fill='white', font=font)
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
        logo_image.save(temp_file.name, 'PNG')
        return temp_file.name

def test_branding_with_logo():
    """Test branding with actual logo file"""
    print("🧪 Testing Branding with Logo File")
    print("=" * 60)
    
    try:
        # Create test logo
        logo_path = create_test_logo()
        print(f"✅ Created test logo: {logo_path}")
        
        # Create or get test user
        test_user, created = User.objects.get_or_create(
            username='test_branding_with_logo',
            defaults={
                'email': 'test@brandingwithlogo.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        # Create or get company profile
        company_profile, created = CompanyProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'company_name': 'Test Textile Company',
                'whatsapp_number': '+1234567890',
                'email': 'contact@testcompany.com',
                'facebook_link': 'https://facebook.com/testcompany',
                'description': 'A test textile company for branding verification',
                'preferred_logo_position': 'top_right'
            }
        )
        
        # Upload logo to company profile
        with open(logo_path, 'rb') as logo_file:
            company_profile.logo.save(
                'test_logo.png',
                File(logo_file),
                save=True
            )
        
        print(f"✅ Logo uploaded to company profile")
        
        # Check profile completeness
        print(f"\n🔍 Company Profile Details:")
        print(f"   Company Name: {company_profile.company_name}")
        print(f"   Has Logo: {bool(company_profile.logo)}")
        print(f"   Logo Path: {company_profile.logo.path if company_profile.logo else 'None'}")
        print(f"   Contact Info: {company_profile.get_contact_info()}")
        print(f"   Profile Complete: {company_profile.has_complete_profile}")
        
        # Test AI poster service
        ai_service = AIPosterService()
        
        if not ai_service.is_available():
            print("❌ AI Poster Service is not available")
            return False
        
        print("✅ AI Poster Service is available")
        
        # Generate poster with branding
        print(f"\n🔍 Testing Poster Generation with Logo:")
        test_prompt = "Create a beautiful textile poster for a silk saree collection"
        
        result = ai_service.generate_from_prompt(test_prompt, "4:5", test_user)
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Branding Applied: {result.get('branding_applied', False)}")
            print(f"   Logo Added: {result.get('logo_added', False)}")
            print(f"   Contact Info Added: {result.get('contact_info_added', False)}")
            
            if result.get('branding_applied'):
                print("✅ Branding was successfully applied!")
                print("✅ Logo and contact details should be visible in the generated poster")
                print(f"✅ Final branded poster: {result.get('image_url')}")
            else:
                print("❌ Branding was not applied")
                print("   Debugging information:")
                print(f"   - Company profile complete: {company_profile.has_complete_profile}")
                print(f"   - Has logo: {bool(company_profile.logo)}")
                print(f"   - Contact info: {bool(company_profile.get_contact_info())}")
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
        # Clean up
        os.unlink(logo_path)
        print("✅ Test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    print("🚀 Starting Branding with Logo Test")
    print("=" * 60)
    
    test_passed = test_branding_with_logo()
    
    if test_passed:
        print("\n🎉 TEST PASSED!")
        print("✅ Branding with logo is working correctly")
        print("✅ Logo and contact details will be added to generated posters")
    else:
        print("\n❌ TEST FAILED!")
        print("Please check the implementation and try again")
    
    print("\n" + "=" * 60)
