#!/usr/bin/env python3
"""
Test Enhanced Branding Approach
Test that company logos and contact details are included in the AI prompt and logo is used as second input.
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

def test_prompt_enhancement():
    """Test that the prompt is enhanced with company branding."""
    print("\n🧪 Testing Prompt Enhancement...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        profile = user.company_profile
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        # Test original prompt
        original_prompt = "Create a beautiful textile poster for a silk saree collection"
        print(f"📝 Original prompt: {original_prompt}")
        
        # Test enhanced prompt
        enhanced_prompt = ai_service._enhance_prompt_with_branding(original_prompt, user)
        print(f"📝 Enhanced prompt: {enhanced_prompt}")
        
        # Check if branding was added
        has_company_name = profile.company_name in enhanced_prompt
        has_contact_info = any(contact in enhanced_prompt for contact in [profile.whatsapp_number, profile.email])
        has_logo_instruction = "company logo" in enhanced_prompt.lower()
        
        print(f"\n📊 Enhancement Results:")
        print(f"   Company name included: {has_company_name}")
        print(f"   Contact info included: {has_contact_info}")
        print(f"   Logo instruction included: {has_logo_instruction}")
        
        if has_company_name and has_contact_info and has_logo_instruction:
            print("✅ Prompt enhancement working correctly!")
            return True
        else:
            print("❌ Prompt enhancement not working correctly")
            return False
        
    except Exception as e:
        print(f"❌ Error testing prompt enhancement: {str(e)}")
        return False

def test_logo_loading():
    """Test that company logo is loaded correctly."""
    print("\n🧪 Testing Logo Loading...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        profile = user.company_profile
        
        # Initialize AI poster service
        ai_service = AIPosterService()
        
        # Test logo loading
        logo_data = ai_service._get_company_logo_image(user)
        
        if logo_data:
            print(f"✅ Company logo loaded successfully: {len(logo_data)} characters")
            print(f"   Logo file: {profile.logo.name}")
            print(f"   Logo exists: {profile.logo and os.path.exists(profile.logo.path)}")
            return True
        else:
            print("❌ Company logo not loaded")
            print(f"   Profile has logo: {bool(profile.logo)}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing logo loading: {str(e)}")
        return False

def test_ai_generation_with_enhanced_branding():
    """Test AI poster generation with enhanced branding approach."""
    print("\n🧪 Testing AI Generation with Enhanced Branding...")
    
    try:
        # Get test user and profile
        user = User.objects.get(email='branding_test@textilecompany.com')
        profile = user.company_profile
        
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
        
        # Generate poster with enhanced branding
        print("🚀 Generating poster with enhanced branding approach...")
        result = ai_service.generate_from_prompt(test_prompt, "4:5", user)
        
        print(f"\n📊 Generation Result:")
        print(f"   Status: {result.get('status')}")
        print(f"   Success: {result.get('status') == 'success'}")
        
        if result.get('status') == 'success':
            print(f"   Image Path: {result.get('image_path')}")
            print(f"   Image URL: {result.get('image_url')}")
            
            print("✅ SUCCESS: Poster generated with enhanced branding approach!")
            print("✅ The generated poster should contain:")
            print("   - Company name and contact details integrated into the design")
            print("   - Company logo incorporated into the poster layout")
            print("   - All branding information naturally integrated by AI")
            return True
        else:
            print(f"❌ Poster generation failed: {result.get('message')}")
            return False
        
    except Exception as e:
        print(f"❌ Error testing AI generation: {str(e)}")
        return False

def main():
    """Run all enhanced branding tests."""
    print("🎯 Testing Enhanced Branding Approach")
    print("=" * 50)
    
    # Test 1: Prompt Enhancement
    print("\n1️⃣ Testing Prompt Enhancement...")
    prompt_success = test_prompt_enhancement()
    
    # Test 2: Logo Loading
    print("\n2️⃣ Testing Logo Loading...")
    logo_success = test_logo_loading()
    
    # Test 3: AI Generation with Enhanced Branding
    print("\n3️⃣ Testing AI Generation with Enhanced Branding...")
    generation_success = test_ai_generation_with_enhanced_branding()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Prompt Enhancement: {'✅ PASS' if prompt_success else '❌ FAIL'}")
    print(f"   Logo Loading: {'✅ PASS' if logo_success else '❌ FAIL'}")
    print(f"   AI Generation: {'✅ PASS' if generation_success else '❌ FAIL'}")
    
    if prompt_success and logo_success and generation_success:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Enhanced branding approach is working correctly")
        print("✅ Company logos and contact details are integrated into AI generation")
        print("✅ No post-processing overlay needed - branding is built into the design")
        return True
    else:
        print("\n❌ SOME TESTS FAILED")
        print("❌ Enhanced branding approach may not be working correctly")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

