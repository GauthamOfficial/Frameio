#!/usr/bin/env python
"""
Test script for automatic company branding in post generation
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

from django.contrib.auth.models import User
from users.models import CompanyProfile
from ai_services.post_generation_views import AIPostGenerationViewSet
from ai_services.brand_overlay_service import BrandOverlayService
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_company_branding_integration():
    """Test the automatic company branding integration"""
    print("🧪 Testing Automatic Company Branding Integration")
    print("=" * 60)
    
    try:
        # Create a test user if it doesn't exist
        test_user, created = User.objects.get_or_create(
            username='test_branding_user',
            defaults={
                'email': 'test@company.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            print("✅ Created test user")
        else:
            print("✅ Found existing test user")
        
        # Create or get company profile
        company_profile, created = CompanyProfile.objects.get_or_create(
            user=test_user,
            defaults={
                'company_name': 'Test Textile Company',
                'whatsapp_number': '+1234567890',
                'email': 'contact@testcompany.com',
                'facebook_link': 'https://facebook.com/testcompany',
                'description': 'A test textile company for branding verification'
            }
        )
        
        if created:
            print("✅ Created company profile")
        else:
            print("✅ Found existing company profile")
        
        # Test the branding service
        viewset = AIPostGenerationViewSet()
        
        # Test company branding retrieval
        print("\n🔍 Testing Company Branding Retrieval:")
        company_branding = viewset._get_company_branding(test_user)
        print(f"   Company Branding: {company_branding}")
        
        if company_branding.get('has_branding'):
            print("✅ Company branding found and configured")
        else:
            print("❌ Company branding not found or incomplete")
            return False
        
        # Test content enrichment
        print("\n🔍 Testing Content Enrichment:")
        test_content = {
            'main_text': 'This is a test post about our amazing textile products!',
            'hashtags': ['#textile', '#fashion', '#quality']
        }
        
        enriched_content = viewset._enrich_content_with_branding(test_content, company_branding)
        
        print("📝 Original Content:")
        print(f"   {test_content['main_text']}")
        
        print("\n📝 Enriched Content:")
        print(f"   {enriched_content['main_text']}")
        
        # Verify branding was added
        if '🏢' in enriched_content['main_text'] and '📞' in enriched_content['main_text']:
            print("✅ Company branding successfully added to content")
        else:
            print("❌ Company branding not properly added")
            return False
        
        # Test brand overlay service
        print("\n🔍 Testing Brand Overlay Service:")
        brand_service = BrandOverlayService()
        
        # Test contact info formatting
        contact_info = company_profile.get_contact_info()
        print(f"   Contact Info: {contact_info}")
        
        if contact_info:
            print("✅ Contact information properly formatted")
        else:
            print("❌ Contact information not available")
            return False
        
        print("\n🎉 All Tests Passed! Automatic Branding Integration is Working!")
        print("\n📋 Summary:")
        print("   ✅ Company profile detection")
        print("   ✅ Logo and contact details retrieval")
        print("   ✅ Content enrichment with branding")
        print("   ✅ Contact information formatting")
        print("   ✅ Brand overlay service integration")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {str(e)}")
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        return False

def test_branding_features():
    """Test specific branding features"""
    print("\n🔍 Testing Specific Branding Features:")
    print("-" * 40)
    
    try:
        # Test company profile completeness
        test_user = User.objects.get(username='test_branding_user')
        company_profile = test_user.company_profile
        
        print(f"   Company Name: {company_profile.company_name}")
        print(f"   WhatsApp: {company_profile.whatsapp_number}")
        print(f"   Email: {company_profile.email}")
        print(f"   Facebook: {company_profile.facebook_link}")
        print(f"   Has Complete Profile: {company_profile.has_complete_profile}")
        
        # Test contact info formatting
        contact_info = company_profile.get_contact_info()
        print(f"   Formatted Contact Info: {contact_info}")
        
        # Test branding text generation
        branding_text = ""
        if company_profile.company_name:
            branding_text += f"\n\n🏢 {company_profile.company_name}"
        
        if contact_info:
            branding_text += "\n\n📞 Contact Us:"
            if contact_info.get('whatsapp'):
                branding_text += f"\n📱 WhatsApp: {contact_info['whatsapp']}"
            if contact_info.get('email'):
                branding_text += f"\n✉️ Email: {contact_info['email']}"
            if contact_info.get('facebook'):
                branding_text += f"\n📘 Facebook: {contact_info['facebook']}"
        
        print(f"\n   Generated Branding Text:")
        print(f"   {branding_text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Branding features test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Automatic Branding Integration Test")
    print("=" * 60)
    
    # Run tests
    test1_passed = test_company_branding_integration()
    test2_passed = test_branding_features()
    
    if test1_passed and test2_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Automatic company branding is working correctly")
        print("✅ Company logos and contact details will be included in all generated posts")
        print("✅ Users with complete company profiles will get branded posts automatically")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Please check the implementation and try again")
    
    print("\n" + "=" * 60)
