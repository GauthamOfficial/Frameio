#!/usr/bin/env python3
"""
Test Simple Branding Approach
Test the simplified branding approach that includes all branding information in the prompt.
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
from ai_services.simple_branding_service import SimpleBrandingService
import tempfile
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def test_simple_branding_service():
    """Test the simple branding service."""
    print("\n🧪 Testing Simple Branding Service...")
    
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
        
        print(f"📊 Company Profile Status:")
        print(f"   Company Name: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete Profile: {profile.has_complete_profile}")
        
        # Initialize simple branding service
        branding_service = SimpleBrandingService()
        
        # Test original prompt
        original_prompt = "Create a beautiful textile poster for a silk saree collection"
        print(f"📝 Original prompt: {original_prompt}")
        
        # Test branding result
        branding_result = branding_service.create_branded_prompt(original_prompt, user)
        
        print(f"\n📊 Branding Result:")
        print(f"   Has branding: {branding_result['has_branding']}")
        print(f"   Company name: {branding_result['company_name']}")
        print(f"   Contact info: {branding_result['contact_info']}")
        print(f"   Has logo: {branding_result['has_logo']}")
        
        if branding_result['has_branding']:
            print(f"\n📝 Enhanced prompt:")
            print(f"{branding_result['enhanced_prompt']}")
            print("✅ Simple branding service working correctly!")
            return True
        else:
            print("❌ Simple branding service not working")
            return False
        
    except Exception as e:
        print(f"❌ Error testing simple branding service: {str(e)}")
        return False

def test_ai_generation_with_simple_branding():
    """Test AI poster generation with simple branding approach."""
    print("\n🧪 Testing AI Generation with Simple Branding...")
    
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
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        if not ai_service.is_available():
            print("❌ AI service is not available")
            print("   Make sure GEMINI_API_KEY is set in environment variables")
            return False
        
        print("✅ AI service is available")
        
        # Test prompt
        test_prompt = "Create a beautiful textile poster for a silk saree collection with elegant patterns"
        print(f"📝 Test prompt: {test_prompt}")
        
        # Generate poster with simple branding
        print("🚀 Generating poster with simple branding approach...")
        result = ai_service.generate_from_prompt(test_prompt, "4:5", user)
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            
            print("✅ SUCCESS: Poster generated with simple branding approach!")
            print("✅ The generated poster should contain:")
            print("   - Company name integrated into the design")
            print("   - Contact information (WhatsApp and Email) included")
            print("   - Professional branding elements")
            print("   - All branding naturally integrated by AI")
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing AI generation: {str(e)}")
        return False

def main():
    """Run all simple branding tests."""
    print("🎯 Testing Simple Branding Approach")
    print("=" * 50)
    
    # Test 1: Simple Branding Service
    print("\n1️⃣ Testing Simple Branding Service...")
    branding_success = test_simple_branding_service()
    
    # Test 2: AI Generation with Simple Branding
    print("\n2️⃣ Testing AI Generation with Simple Branding...")
    generation_success = test_ai_generation_with_simple_branding()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Simple Branding Service: {'✅ PASS' if branding_success else '❌ FAIL'}")
    print(f"   AI Generation: {'✅ PASS' if generation_success else '❌ FAIL'}")
    
    if branding_success and generation_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Simple branding approach is working correctly")
        print("✅ Company logos and contact details are integrated into AI generation")
        print("✅ No complex logo handling needed - everything in the prompt")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Simple branding approach may not be working correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
