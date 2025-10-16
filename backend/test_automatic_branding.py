#!/usr/bin/env python3
"""
Test Automatic Branding Integration
Tests that company logos and contact details are automatically added to generated posters.
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
from ai_services.brand_overlay_service import BrandOverlayService
import tempfile
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def create_test_user_and_profile():
    """Create a test user with complete company profile."""
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
        
        # Create a simple test logo
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
        
        print(f"✅ Company Profile Status:")
        print(f"   Company Name: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete Profile: {profile.has_complete_profile}")
        
        return user, profile
        
    except Exception as e:
        print(f"❌ Error creating test user and profile: {str(e)}")
        return None, None

def test_brand_overlay_service():
    """Test the brand overlay service directly."""
    print("\n🧪 Testing Brand Overlay Service...")
    
    try:
        # Create a test poster image
        poster_img = Image.new('RGB', (800, 600), color='lightblue')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(poster_img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        draw.text((200, 250), "AI Generated Textile Poster", fill='darkblue', font=font)
        
        # Save test poster to temporary file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            poster_img.save(temp_file.name, format='PNG')
            temp_poster_path = temp_file.name
        
        print(f"✅ Test poster created: {temp_poster_path}")
        
        # Get test user and profile
        user, profile = create_test_user_and_profile()
        if not user or not profile:
            return False
        
        # Test brand overlay service
        overlay_service = BrandOverlayService()
        
        # Test brand overlay
        result = overlay_service.add_brand_overlay(
            temp_poster_path,
            profile,
            "test_branded_poster.png"
        )
        
        print(f"\n📊 Brand Overlay Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Image Path: {result.get('image_path')}")
        print(f"   Image URL: {result.get('image_url')}")
        print(f"   Branding Applied: {result.get('branding_applied')}")
        print(f"   Logo Added: {result.get('logo_added')}")
        print(f"   Contact Info Added: {result.get('contact_info_added')}")
        
        if result.get('status') == 'success':
            print("✅ Brand overlay applied successfully!")
            print("✅ Logo and contact information should be visible in the final image")
            return True
        else:
            print(f"❌ Brand overlay failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing brand overlay service: {str(e)}")
        return False
    finally:
        # Clean up temporary file
        try:
            if 'temp_poster_path' in locals():
                os.unlink(temp_poster_path)
        except:
            pass

def test_ai_poster_generation_with_branding():
    """Test AI poster generation with automatic branding."""
    print("\n🧪 Testing AI Poster Generation with Branding...")
    
    try:
        # Get test user and profile
        user, profile = create_test_user_and_profile()
        if not user or not profile:
            return False
        
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
        
        # Generate poster with branding
        print("🚀 Generating poster with automatic branding...")
        result = ai_service.generate_from_prompt(test_prompt, "4:5", user)
        
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
                print("✅ SUCCESS: Branding was automatically applied!")
                print("✅ The generated poster should contain:")
                print("   - Company logo in the preferred position")
                print("   - Contact information (WhatsApp, Email, Facebook)")
                print("   - Company name")
                return True
            else:
                print("❌ Branding was not applied")
                print("   This might be because:")
                print("   - Company profile is incomplete")
                print("   - Logo file is missing or corrupted")
                print("   - Brand overlay service error")
                return False
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing AI poster generation: {str(e)}")
        return False

def main():
    """Run all branding tests."""
    print("🎯 Testing Automatic Branding Integration")
    print("=" * 50)
    
    # Test 1: Brand Overlay Service
    print("\n1️⃣ Testing Brand Overlay Service...")
    overlay_success = test_brand_overlay_service()
    
    # Test 2: AI Poster Generation with Branding
    print("\n2️⃣ Testing AI Poster Generation with Branding...")
    generation_success = test_ai_poster_generation_with_branding()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Brand Overlay Service: {'✅ PASS' if overlay_success else '❌ FAIL'}")
    print(f"   AI Poster Generation: {'✅ PASS' if generation_success else '❌ FAIL'}")
    
    if overlay_success and generation_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Automatic branding is working correctly")
        print("✅ Company logos and contact details are automatically added to generated posters")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Automatic branding may not be working correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)