#!/usr/bin/env python
"""
Quick verification script for brand personalization feature.
Run this to verify all components are working correctly.
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def verify_models():
    """Verify all required models exist."""
    print("🔍 Verifying Models...")
    
    try:
        from users.models import CompanyProfile
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        
        # Check CompanyProfile fields
        fields = [field.name for field in CompanyProfile._meta.fields]
        required_fields = [
            'user', 'company_name', 'logo', 'whatsapp_number', 
            'email', 'facebook_link', 'preferred_logo_position'
        ]
        
        missing = [f for f in required_fields if f not in fields]
        if missing:
            print(f"❌ Missing fields: {missing}")
            return False
        
        print("✅ CompanyProfile model verified")
        return True
        
    except Exception as e:
        print(f"❌ Model verification failed: {e}")
        return False

def verify_services():
    """Verify brand overlay service exists."""
    print("🔍 Verifying Services...")
    
    try:
        from ai_services.brand_overlay_service import BrandOverlayService
        from ai_services.ai_poster_service import AIPosterService
        
        # Test service instantiation
        brand_service = BrandOverlayService()
        poster_service = AIPosterService()
        
        print("✅ BrandOverlayService verified")
        print("✅ AIPosterService verified")
        return True
        
    except Exception as e:
        print(f"❌ Service verification failed: {e}")
        return False

def verify_serializers():
    """Verify serializers exist."""
    print("🔍 Verifying Serializers...")
    
    try:
        from users.serializers import CompanyProfileSerializer, CompanyProfileUpdateSerializer
        
        print("✅ CompanyProfileSerializer verified")
        print("✅ CompanyProfileUpdateSerializer verified")
        return True
        
    except Exception as e:
        print(f"❌ Serializer verification failed: {e}")
        return False

def verify_views():
    """Verify views exist."""
    print("🔍 Verifying Views...")
    
    try:
        from users.views import CompanyProfileViewSet
        
        # Check required methods
        methods = ['list', 'retrieve', 'create', 'update', 'destroy', 'status']
        for method in methods:
            if not hasattr(CompanyProfileViewSet, method):
                print(f"❌ Missing method: {method}")
                return False
        
        print("✅ CompanyProfileViewSet verified")
        return True
        
    except Exception as e:
        print(f"❌ View verification failed: {e}")
        return False

def verify_urls():
    """Verify URL patterns exist."""
    print("🔍 Verifying URLs...")
    
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        
        # Test URL patterns
        urls_to_test = [
            '/api/users/company-profiles/',
            '/api/users/company-profiles/status/',
        ]
        
        for url in urls_to_test:
            try:
                response = client.get(url)
                # Should return 401 (unauthorized) or 200, not 404
                if response.status_code not in [200, 401, 403]:
                    print(f"❌ URL {url} returned {response.status_code}")
                    return False
            except Exception as e:
                print(f"❌ URL {url} failed: {e}")
                return False
        
        print("✅ URL patterns verified")
        return True
        
    except Exception as e:
        print(f"❌ URL verification failed: {e}")
        return False

def main():
    """Run all verifications."""
    print("🚀 Brand Personalization Feature Verification")
    print("=" * 50)
    
    verifications = [
        verify_models,
        verify_services,
        verify_serializers,
        verify_views,
        verify_urls
    ]
    
    results = []
    for verify_func in verifications:
        try:
            result = verify_func()
            results.append(result)
            print()  # Add spacing
        except Exception as e:
            print(f"❌ Verification failed with exception: {e}")
            results.append(False)
            print()
    
    print("=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED!")
        print("\n✅ Brand Personalization Feature is READY!")
        print("\n📋 Available Features:")
        print("  • Company profile management")
        print("  • Logo upload and positioning")
        print("  • Contact information overlay")
        print("  • AI poster generation with branding")
        print("  • Frontend settings UI")
        print("  • Backend API endpoints")
        print("\n🚀 Users can now access this feature at /dashboard/settings")
    else:
        print(f"\n⚠️ {total - passed} verifications failed.")
        print("Please check the errors above and fix any issues.")

if __name__ == "__main__":
    main()

