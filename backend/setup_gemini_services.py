#!/usr/bin/env python3
"""
Setup script for Google Gemini AI services
Creates Gemini provider and initializes the service
"""
import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.models import AIProvider
from organizations.models import Organization
from users.models import User
from django.conf import settings


def setup_gemini_services():
    """Setup Google Gemini AI services"""
    print("🚀 Setting up Google Gemini AI Services...")
    
    # Check if API keys are configured
    if not settings.GEMINI_API_KEY and not settings.GOOGLE_API_KEY:
        print("❌ Error: Google Gemini API key not configured")
        print("Please set GEMINI_API_KEY or GOOGLE_API_KEY in your environment variables")
        return False
    
    # Create or update Gemini provider
    provider, created = AIProvider.objects.get_or_create(
        name='gemini',
        defaults={
            'api_key': settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY,
            'api_url': 'https://generativelanguage.googleapis.com/v1beta',
            'is_active': True,
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000
        }
    )
    
    if created:
        print(f"✅ Created Gemini provider: {provider.get_name_display()}")
    else:
        # Update existing provider
        provider.api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
        provider.api_url = 'https://generativelanguage.googleapis.com/v1beta'
        provider.is_active = True
        provider.save()
        print(f"✅ Updated Gemini provider: {provider.get_name_display()}")
    
    # Create test organization if it doesn't exist
    test_org, org_created = Organization.objects.get_or_create(
        name='Test Organization',
        defaults={
            'description': 'Test organization for Gemini AI services',
            'is_active': True
        }
    )
    
    if org_created:
        print(f"✅ Created test organization: {test_org.name}")
    else:
        print(f"✅ Using existing organization: {test_org.name}")
    
    # Create test user if it doesn't exist
    test_user, user_created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True,
            'organization': test_org
        }
    )
    
    if user_created:
        print(f"✅ Created test user: {test_user.email}")
    else:
        print(f"✅ Using existing user: {test_user.email}")
    
    # Test Gemini service
    print("\n🧪 Testing Gemini service...")
    try:
        from ai_services.gemini_service import gemini_service
        
        # Test basic functionality
        test_result = gemini_service.generate_image(
            prompt="Test image generation",
            width=512,
            height=512
        )
        
        if test_result.get('success'):
            print("✅ Gemini service test successful")
            print(f"   Model: {test_result['data'].get('model_used', 'Unknown')}")
            print(f"   Processing time: {test_result['data'].get('processing_time', 0):.2f}s")
        else:
            print(f"❌ Gemini service test failed: {test_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Gemini service test error: {str(e)}")
    
    print("\n📊 Gemini Services Setup Summary:")
    print(f"   Provider: {provider.get_name_display()}")
    print(f"   Model: {settings.GEMINI_MODEL_NAME}")
    print(f"   API Key: {'✓ Configured' if (settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY) else '✗ Missing'}")
    print(f"   Organization: {test_org.name}")
    print(f"   Test User: {test_user.email}")
    
    print("\n🎉 Gemini services setup complete!")
    print("\nNext steps:")
    print("1. Test the API endpoints:")
    print("   python backend/test_ai_endpoints.py")
    print("2. Run the verification script:")
    print("   python backend/verify_ai_deliverables.py")
    
    return True


if __name__ == '__main__':
    setup_gemini_services()
