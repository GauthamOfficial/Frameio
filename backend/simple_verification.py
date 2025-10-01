#!/usr/bin/env python
"""
Simple verification script to test basic functionality.
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_models():
    """Test that models can be imported and created."""
    print("Testing Models...")
    
    try:
        from organizations.models import Organization, OrganizationMember, OrganizationInvitation
        from users.models import User, UserSession, UserActivity
        
        print("✅ All models imported successfully")
        
        # Test Organization creation
        org = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization'
        )
        print(f"✅ Organization created: {org.name}")
        
        # Test User creation
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ User created: {user.username}")
        
        # Test OrganizationMember creation
        membership = OrganizationMember.objects.create(
            organization=org,
            user=user,
            role='owner'
        )
        print(f"✅ Membership created: {membership.role}")
        
        # Test model methods
        print(f"✅ Organization is_active: {org.is_active}")
        print(f"✅ Organization can_generate_ai: {org.can_generate_ai}")
        print(f"✅ User full_name: {user.full_name}")
        print(f"✅ Membership is_owner: {membership.is_owner}")
        
        # Test usage tracking
        org.increment_ai_usage()
        print(f"✅ AI usage incremented: {org.ai_generations_used}")
        
        # Clean up
        membership.delete()
        user.delete()
        org.delete()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False

def test_authentication():
    """Test authentication system."""
    print("\nTesting Authentication...")
    
    try:
        from users.models import User
        from django.contrib.auth import authenticate
        
        # Create user
        user = User.objects.create_user(
            username='authtest',
            email='authtest@example.com',
            password='testpass123'
        )
        
        # Test authentication
        auth_user = authenticate(username='authtest', password='testpass123')
        
        if auth_user:
            print("✅ User authentication works")
        else:
            print("❌ User authentication failed")
            return False
        
        # Test user properties
        print(f"✅ User email: {user.email}")
        print(f"✅ User is_active: {user.is_active}")
        
        # Clean up
        user.delete()
        print("✅ Authentication test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def test_api_imports():
    """Test that API components can be imported."""
    print("\nTesting API Components...")
    
    try:
        from organizations.serializers import OrganizationSerializer
        from organizations.views import OrganizationViewSet
        from users.authentication import ClerkAuthentication
        
        print("✅ Serializers imported successfully")
        print("✅ Views imported successfully")
        print("✅ Authentication classes imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ API components test failed: {e}")
        return False

def test_settings():
    """Test Django settings."""
    print("\nTesting Django Settings...")
    
    try:
        from django.conf import settings
        
        checks = [
            ('INSTALLED_APPS', 'organizations' in settings.INSTALLED_APPS),
            ('AUTH_USER_MODEL', settings.AUTH_USER_MODEL == 'users.User'),
            ('REST_FRAMEWORK', hasattr(settings, 'REST_FRAMEWORK')),
            ('CORS_HEADERS', 'corsheaders' in settings.INSTALLED_APPS),
            ('DATABASE', settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'),
        ]
        
        for check_name, result in checks:
            if result:
                print(f"✅ {check_name}: OK")
            else:
                print(f"❌ {check_name}: FAILED")
        
        return all(result for _, result in checks)
        
    except Exception as e:
        print(f"❌ Settings test failed: {e}")
        return False

def main():
    """Main verification function."""
    print("🚀 Frameio Multi-Tenant Django Backend - Simple Verification")
    print("=" * 70)
    
    tests = [
        test_models,
        test_authentication,
        test_api_imports,
        test_settings
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 70)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 ALL BASIC FUNCTIONALITY IS WORKING!")
        print("✅ Phase 1, Week 1, Team Member 1 deliverables are functional!")
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
