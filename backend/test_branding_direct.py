#!/usr/bin/env python3
"""
Test Branding Direct
Test the branding system directly to see what's happening.
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

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def test_branding_direct():
    """Test branding directly."""
    print("\n🧪 Testing Branding Direct...")
    
    try:
        # Get the first user with complete profile
        profiles = CompanyProfile.objects.filter(
            logo__isnull=False,
            company_name__isnull=False
        ).exclude(company_name='').exclude(logo='')
        
        if not profiles.exists():
            print("❌ No users with complete profiles found")
            return False
        
        user = profiles.first().user
        profile = profiles.first()
        
        print(f"📊 Using user: {user.username} ({user.email})")
        print(f"   Company: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete: {profile.has_complete_profile}")
        
        # Test 1: AI Poster Service
        print("\n🔍 Test 1: AI Poster Service")
        ai_service = AIPosterService()
        
        if not ai_service.is_available():
            print("❌ AI service is not available")
            return False
        
        print("✅ AI service is available")
        
        # Generate poster
        print("🚀 Generating poster with branding...")
        result = ai_service.generate_from_prompt(
            "Create a beautiful textile poster for a silk saree collection",
            "4:5",
            user
        )
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            print(f"   Branding Applied: {result.get('branding_applied')}")
            print(f"   Logo Added: {result.get('logo_added')}")
            print(f"   Contact Info Added: {result.get('contact_info_added')}")
            
            if result.get('branding_applied'):
                print("✅ SUCCESS: Branding was applied!")
                print("✅ The generated poster should contain logo and contact details!")
                return True
            else:
                print("❌ Branding was not applied")
                print("❌ This is the issue - branding is not working")
                return False
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing branding direct: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the branding direct test."""
    print("🎯 Testing Branding Direct")
    print("=" * 50)
    
    # Test: Branding Direct
    print("\n1️⃣ Testing Branding Direct...")
    branding_success = test_branding_direct()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Branding Direct: {'✅ PASS' if branding_success else '❌ FAIL'}")
    
    if branding_success:
        print("\n🎉 TEST PASSED!")
        print("✅ Branding is working correctly")
        print("✅ The issue might be in the frontend or API call")
        return True
    else:
        print("\n❌ TEST FAILED")
        print("❌ Branding is not working - this is the root cause")
        print("❌ The brand overlay service is not being called or is failing")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

