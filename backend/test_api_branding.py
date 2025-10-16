#!/usr/bin/env python3
"""
Test API Branding
Test the API endpoint directly to see if branding is working.
"""

import os
import sys
import django
import requests
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import CompanyProfile
from PIL import Image
import io

User = get_user_model()

def test_api_branding():
    """Test the API endpoint with branding."""
    print("\n🧪 Testing API Branding...")
    
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
        
        # Test API call
        print("\n🚀 Testing API call...")
        
        # API endpoint
        url = "http://localhost:8000/api/ai/ai-poster/generate_poster/"
        
        # Request data
        data = {
            "prompt": "Create a beautiful textile poster for a silk saree collection",
            "aspect_ratio": "4:5"
        }
        
        # Headers
        headers = {
            'Content-Type': 'application/json',
            'X-Dev-User-ID': str(user.id)  # Pass user ID for testing
        }
        
        print(f"📝 API Request:")
        print(f"   URL: {url}")
        print(f"   Data: {data}")
        print(f"   Headers: {headers}")
        
        # Make API call
        response = requests.post(url, json=data, headers=headers)
        
        print(f"\n📊 API Response:")
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Success: {result.get('success')}")
            print(f"   Message: {result.get('message')}")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Branding Applied: {result.get('branding_applied')}")
            print(f"   Logo Added: {result.get('logo_added')}")
            print(f"   Contact Info Added: {result.get('contact_info_added')}")
            
            if result.get('success'):
                print("✅ API call successful!")
                if result.get('branding_applied'):
                    print("✅ Branding was applied!")
                    print("✅ Logo and contact details should be in the generated poster!")
                    return True
                else:
                    print("❌ Branding was not applied")
                    return False
            else:
                print(f"❌ API call failed: {result.get('error')}")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing API branding: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the API branding test."""
    print("🎯 Testing API Branding")
    print("=" * 50)
    
    # Test: API Branding
    print("\n1️⃣ Testing API Branding...")
    api_success = test_api_branding()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   API Branding: {'✅ PASS' if api_success else '❌ FAIL'}")
    
    if api_success:
        print("\n🎉 TEST PASSED!")
        print("✅ API endpoint is working with branding")
        print("✅ Company logos and contact details are being applied")
        print("✅ The branding system is working correctly")
        return True
    else:
        print("\n❌ TEST FAILED")
        print("❌ API endpoint is not working with branding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
