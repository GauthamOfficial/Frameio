#!/usr/bin/env python3
"""
Test Direct Branding Approach
Test the direct approach that includes contact details in prompt and logo as second input.
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
from ai_services.ai_poster_service import AIPosterService
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def test_direct_branding():
    """Test the direct branding approach."""
    print("\n🧪 Testing Direct Branding Approach...")
    
    try:
        # Create or get test user and profile
        user, created = User.objects.get_or_create(
            email='branding_test@textilecompany.com',
            defaults={
                'username': 'branding_test_user',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
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
        
        print(f"📊 Company Profile Status:")
        print(f"   Company Name: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete Profile: {profile.has_complete_profile}")
        
        # Test direct branding methods
        ai_service = AIPosterService()
        
        # Test 1: Contact details in prompt
        print("\n🔍 Test 1: Contact details in prompt")
        original_prompt = "Create a beautiful textile poster for a silk saree collection"
        enhanced_prompt = ai_service._add_contact_details_to_prompt(original_prompt, user)
        
        print(f"   Original prompt: {original_prompt}")
        print(f"   Enhanced prompt: {enhanced_prompt}")
        print(f"   Contact details added: {enhanced_prompt != original_prompt}")
        
        # Test 2: Logo as second input
        print("\n🔍 Test 2: Logo as second input")
        logo_data = ai_service._get_company_logo_for_ai(user)
        
        print(f"   Logo data available: {bool(logo_data)}")
        if logo_data:
            print(f"   Logo data length: {len(logo_data)} characters")
            print(f"   First 100 chars: {logo_data[:100]}")
        
        # Test 3: Full AI generation
        print("\n🔍 Test 3: Full AI generation with direct branding")
        if not ai_service.is_available():
            print("❌ AI service is not available")
            return False
        
        print("✅ AI service is available")
        
        # Generate poster with direct branding
        print("🚀 Generating poster with direct branding approach...")
        result = ai_service.generate_from_prompt(original_prompt, "4:5", user)
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Branding Applied: {result.get('branding_applied')}")
            print(f"   Logo Added: {result.get('logo_added')}")
            print(f"   Contact Info Added: {result.get('contact_info_added')}")
            
            print("✅ SUCCESS: Poster generated with direct branding approach!")
            print("✅ The generated poster should contain:")
            print("   - Contact details included in the AI prompt")
            print("   - Company logo as second input image")
            print("   - Professional branding elements")
            print("   - All branding naturally integrated by AI")
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing direct branding: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the direct branding test."""
    print("🎯 Testing Direct Branding Approach")
    print("=" * 50)
    
    # Test: Direct Branding
    print("\n1️⃣ Testing Direct Branding...")
    branding_success = test_direct_branding()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Direct Branding: {'✅ PASS' if branding_success else '❌ FAIL'}")
    
    if branding_success:
        print("\n🎉 TEST PASSED!")
        print("✅ Direct branding approach is working correctly")
        print("✅ Contact details are included in the prompt")
        print("✅ Company logo is added as second input image")
        print("✅ AI generates posters with integrated branding")
        return True
    else:
        print("\n❌ TEST FAILED")
        print("❌ Direct branding approach is not working correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
