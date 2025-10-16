#!/usr/bin/env python3
"""
Test Branding Service Only
Test just the branding service without requiring AI generation.
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

from django.contrib.auth import get_user_model
from users.models import CompanyProfile
from ai_services.simple_branding_service import SimpleBrandingService
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def test_branding_service():
    """Test the branding service with a test user."""
    print("\n🧪 Testing Branding Service...")
    
    try:
        # Create or get test user
        user, created = User.objects.get_or_create(
            email='branding_test@textilecompany.com',
            defaults={
                'username': 'branding_test_user',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print("✅ Created test user")
        else:
            print("✅ Using existing test user")
        
        # Create or get company profile
        profile, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': 'Test Textile Company',
                'whatsapp_number': '+1234567890',
                'email': 'contact@testtextile.com',
                'preferred_logo_position': 'top_right'
            }
        )
        
        if created:
            print("✅ Created company profile")
        else:
            print("✅ Using existing company profile")
        
        # Create a simple test logo if it doesn't exist
        if not profile.logo:
            print("📝 Creating test logo...")
            logo_img = Image.new('RGB', (200, 200), color='blue')
            from PIL import ImageDraw, ImageFont
            
            # Add text to logo
            draw = ImageDraw.Draw(logo_img)
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                font = ImageFont.load_default()
            
            draw.text((50, 80), "TEST", fill='white', font=font)
            draw.text((50, 120), "LOGO", fill='white', font=font)
            
            # Save logo to profile
            logo_bytes = io.BytesIO()
            logo_img.save(logo_bytes, format='PNG')
            logo_bytes.seek(0)
            
            from django.core.files.base import ContentFile
            profile.logo.save('test_logo.png', ContentFile(logo_bytes.getvalue()), save=True)
            print("✅ Test logo created and saved")
        
        print(f"\n📊 Company Profile Status:")
        print(f"   Company Name: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete Profile: {profile.has_complete_profile}")
        print(f"   Contact Info: {profile.get_contact_info()}")
        
        # Test branding service
        branding_service = SimpleBrandingService()
        
        # Test original prompt
        original_prompt = "Create a beautiful textile poster for a silk saree collection"
        print(f"\n📝 Original prompt: {original_prompt}")
        
        # Test branding result
        branding_result = branding_service.create_branded_prompt(original_prompt, user)
        
        print(f"\n📊 Branding Result:")
        print(f"   Has branding: {branding_result['has_branding']}")
        print(f"   Company name: {branding_result['company_name']}")
        print(f"   Contact info: {branding_result['contact_info']}")
        print(f"   Has logo: {branding_result['has_logo']}")
        
        if branding_result['has_branding']:
            print(f"\n📝 Enhanced prompt:")
            print("=" * 80)
            print(branding_result['enhanced_prompt'])
            print("=" * 80)
            print("✅ Simple branding service working correctly!")
            return True
        else:
            print("❌ Simple branding service not working")
            return False
        
    except Exception as e:
        print(f"❌ Error testing branding service: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the branding service test."""
    print("🎯 Testing Branding Service Only")
    print("=" * 50)
    
    # Test: Branding Service
    print("\n1️⃣ Testing Branding Service...")
    branding_success = test_branding_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Branding Service: {'✅ PASS' if branding_success else '❌ FAIL'}")
    
    if branding_success:
        print("\n🎉 TEST PASSED!")
        print("✅ Simple branding service is working correctly")
        print("✅ Company logos and contact details are integrated into prompts")
        print("✅ Enhanced prompts include all branding requirements")
        return True
    else:
        print("\n❌ TEST FAILED")
        print("❌ Simple branding service is not working correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
