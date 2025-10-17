#!/usr/bin/env python3
"""
Debug Branding Implementation
Debug why logos and contact details are not appearing in generated posters.
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
import tempfile
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

User = get_user_model()

def debug_company_profile():
    """Debug company profile data."""
    print("\n🔍 Debugging Company Profile...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        profile = user.company_profile
        
        print(f"📊 Company Profile Debug:")
        print(f"   User: {user.username} ({user.email})")
        print(f"   Company Name: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   Logo exists: {profile.logo and os.path.exists(profile.logo.path) if profile.logo else False}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Has complete profile: {profile.has_complete_profile}")
        print(f"   Contact info: {profile.get_contact_info()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging company profile: {str(e)}")
        return False

def debug_prompt_enhancement():
    """Debug prompt enhancement."""
    print("\n🔍 Debugging Prompt Enhancement...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        # Test original prompt
        original_prompt = "Create a beautiful textile poster for a silk saree collection"
        print(f"📝 Original prompt: {original_prompt}")
        
        # Test enhanced prompt
        enhanced_prompt = ai_service._enhance_prompt_with_branding(original_prompt, user)
        print(f"📝 Enhanced prompt: {enhanced_prompt}")
        
        # Check if enhancement worked
        if enhanced_prompt != original_prompt:
            print("✅ Prompt was enhanced with branding")
            return True
        else:
            print("❌ Prompt was not enhanced")
            return False
        
    except Exception as e:
        print(f"❌ Error debugging prompt enhancement: {str(e)}")
        return False

def debug_logo_loading():
    """Debug logo loading."""
    print("\n🔍 Debugging Logo Loading...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        profile = user.company_profile
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        # Test logo loading
        logo_data = ai_service._get_company_logo_image(user)
        
        if logo_data:
            print(f"✅ Logo loaded successfully: {len(logo_data)} characters")
            print(f"   First 100 chars: {logo_data[:100]}")
            return True
        else:
            print("❌ Logo not loaded")
            print(f"   Profile has logo: {bool(profile.logo)}")
            if profile.logo:
                print(f"   Logo path: {profile.logo.path}")
                print(f"   Logo exists: {os.path.exists(profile.logo.path)}")
            return False
        
    except Exception as e:
        print(f"❌ Error debugging logo loading: {str(e)}")
        return False

def debug_ai_generation():
    """Debug AI generation with detailed logging."""
    print("\n🔍 Debugging AI Generation...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        if not ai_service.is_available():
            print("❌ AI service is not available")
            return False
        
        print("✅ AI service is available")
        
        # Test prompt
        test_prompt = "Create a beautiful textile poster for a silk saree collection"
        print(f"📝 Test prompt: {test_prompt}")
        
        # Generate poster with detailed logging
        print("🚀 Generating poster with detailed logging...")
        result = ai_service.generate_from_prompt(test_prompt, "4:5", user)
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            print("✅ Poster generated successfully")
            print("🔍 Check the generated image to see if branding is included")
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error debugging AI generation: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all debugging tests."""
    print("🔍 Debugging Branding Implementation")
    print("=" * 50)
    
    # Debug 1: Company Profile
    print("\n1️⃣ Debugging Company Profile...")
    profile_success = debug_company_profile()
    
    # Debug 2: Prompt Enhancement
    print("\n2️⃣ Debugging Prompt Enhancement...")
    prompt_success = debug_prompt_enhancement()
    
    # Debug 3: Logo Loading
    print("\n3️⃣ Debugging Logo Loading...")
    logo_success = debug_logo_loading()
    
    # Debug 4: AI Generation
    print("\n4️⃣ Debugging AI Generation...")
    generation_success = debug_ai_generation()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEBUG SUMMARY:")
    print(f"   Company Profile: {'✅ OK' if profile_success else '❌ FAIL'}")
    print(f"   Prompt Enhancement: {'✅ OK' if prompt_success else '❌ FAIL'}")
    print(f"   Logo Loading: {'✅ OK' if logo_success else '❌ FAIL'}")
    print(f"   AI Generation: {'✅ OK' if generation_success else '❌ FAIL'}")
    
    if profile_success and prompt_success and logo_success and generation_success:
        print("\n🎉 ALL DEBUGS PASSED!")
        print("✅ The branding implementation should be working")
        print("🔍 Check the generated poster to see if branding is included")
    else:
        print("\n❌ SOME DEBUGS FAILED")
        print("❌ There are issues with the branding implementation")
    
    return profile_success and prompt_success and logo_success and generation_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

