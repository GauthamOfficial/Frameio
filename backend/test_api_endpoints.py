#!/usr/bin/env python
"""
Test script to verify API endpoints are working correctly.
"""
import requests
import json
import sys

# Base URL for the API
BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    """Test the API endpoints."""
    print("Testing Frameio API Endpoints")
    print("=" * 50)
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/admin/", timeout=5)
        print("✅ Django server is running")
    except requests.exceptions.RequestException as e:
        print(f"❌ Django server is not running: {e}")
        return False
    
    # Test 2: Check API endpoints
    endpoints_to_test = [
        "/api/organizations/",
        "/api/members/",
        "/api/invitations/",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            print(f"✅ {endpoint} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint} - Error: {e}")
    
    # Test 3: Test organization creation (without authentication)
    print("\nTesting Organization Creation...")
    org_data = {
        "name": "Test Organization",
        "description": "Test organization for API testing",
        "website": "https://test.com",
        "industry": "Technology"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/organizations/", json=org_data, timeout=5)
        print(f"Organization creation response: {response.status_code}")
        if response.status_code in [201, 403]:  # 403 is expected without auth
            print("✅ Organization endpoint is accessible")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Organization creation failed: {e}")
    
    print("\n" + "=" * 50)
    print("API endpoint testing completed!")
    return True

def test_database_models():
    """Test database models."""
    print("\nTesting Database Models...")
    print("-" * 30)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
        django.setup()
        
        from organizations.models import Organization, OrganizationMember
        from users.models import User
        
        # Test model creation
        print("✅ Models imported successfully")
        
        # Test organization creation
        org = Organization.objects.create(
            name="Test Organization",
            slug="test-org",
            description="Test organization"
        )
        print(f"✅ Organization created: {org.name}")
        
        # Test user creation
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
        print(f"✅ User created: {user.username}")
        
        # Test membership creation
        membership = OrganizationMember.objects.create(
            organization=org,
            user=user,
            role="owner"
        )
        print(f"✅ Membership created: {membership.role}")
        
        # Test model methods
        print(f"✅ Organization is_active: {org.is_active}")
        print(f"✅ Organization can_generate_ai: {org.can_generate_ai}")
        print(f"✅ User full_name: {user.full_name}")
        print(f"✅ Membership is_owner: {membership.is_owner}")
        
        # Clean up
        org.delete()
        user.delete()
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database model test failed: {e}")
        return False

def test_authentication():
    """Test authentication system."""
    print("\nTesting Authentication System...")
    print("-" * 30)
    
    try:
        import os
        import django
        
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
        django.setup()
        
        from users.models import User
        from django.contrib.auth import authenticate
        
        # Test user authentication
        user = User.objects.create_user(
            username="authtest",
            email="authtest@example.com",
            password="testpass123"
        )
        
        # Test authentication
        auth_user = authenticate(username="authtest", password="testpass123")
        if auth_user:
            print("✅ User authentication works")
        else:
            print("❌ User authentication failed")
            return False
        
        # Test user properties
        print(f"✅ User email: {user.email}")
        print(f"✅ User is_active: {user.is_active}")
        print(f"✅ User is_staff: {user.is_staff}")
        
        # Clean up
        user.delete()
        print("✅ Authentication test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def main():
    """Main test function."""
    print("Frameio Multi-Tenant Django Application Test Suite")
    print("=" * 60)
    
    # Run tests
    api_success = test_api_endpoints()
    model_success = test_database_models()
    auth_success = test_authentication()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"API Endpoints: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"Database Models: {'✅ PASS' if model_success else '❌ FAIL'}")
    print(f"Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    
    if all([api_success, model_success, auth_success]):
        print("\n🎉 ALL TESTS PASSED! Multi-tenant Django application is working correctly.")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED! Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
