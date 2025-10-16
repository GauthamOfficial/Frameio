#!/usr/bin/env python3
"""
Test Frontend Authentication
Test if the frontend authentication is working with the API.
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

User = get_user_model()

def test_frontend_auth():
    """Test frontend authentication with API."""
    print("\n🧪 Testing Frontend Authentication...")
    
    try:
        # Get the first user with a complete company profile
        company_profiles = CompanyProfile.objects.filter(
            logo__isnull=False,
            company_name__isnull=False
        ).exclude(company_name='').exclude(logo='')
        
        if not company_profiles.exists():
            print("❌ No users with complete company profiles found")
            return False
        
        user = company_profiles.first().user
        profile = company_profiles.first()
        
        print(f"📊 Using user: {user.username} ({user.email})")
        print(f"   Company: {profile.company_name}")
        print(f"   Logo: {profile.logo.name if profile.logo else 'None'}")
        print(f"   WhatsApp: {profile.whatsapp_number}")
        print(f"   Email: {profile.email}")
        print(f"   Complete Profile: {profile.has_complete_profile}")
        
        # Test API call with different authentication methods
        url = "http://localhost:8000/api/ai/ai-poster/generate_poster/"
        data = {
            "prompt": "Create a beautiful textile poster for a silk saree collection",
            "aspect_ratio": "4:5"
        }
        
        # Test 1: No authentication
        print("\n🔍 Test 1: No authentication")
        response1 = requests.post(url, json=data)
        print(f"   Status: {response1.status_code}")
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"   Success: {result1.get('success')}")
            print(f"   Branding Applied: {result1.get('branding_applied')}")
            print(f"   Logo Added: {result1.get('logo_added')}")
            print(f"   Contact Info Added: {result1.get('contact_info_added')}")
        
        # Test 2: With user ID header
        print("\n🔍 Test 2: With user ID header")
        headers2 = {
            'Content-Type': 'application/json',
            'X-Dev-User-ID': str(user.id)
        }
        response2 = requests.post(url, json=data, headers=headers2)
        print(f"   Status: {response2.status_code}")
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"   Success: {result2.get('success')}")
            print(f"   Branding Applied: {result2.get('branding_applied')}")
            print(f"   Logo Added: {result2.get('logo_added')}")
            print(f"   Contact Info Added: {result2.get('contact_info_added')}")
        
        # Test 3: With Clerk token (mock)
        print("\n🔍 Test 3: With Clerk token (mock)")
        headers3 = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test_clerk_token'
        }
        response3 = requests.post(url, json=data, headers=headers3)
        print(f"   Status: {response3.status_code}")
        if response3.status_code == 200:
            result3 = response3.json()
            print(f"   Success: {result3.get('success')}")
            print(f"   Branding Applied: {result3.get('branding_applied')}")
            print(f"   Logo Added: {result3.get('logo_added')}")
            print(f"   Contact Info Added: {result3.get('contact_info_added')}")
        
        # Check which test worked
        if response1.status_code == 200 and response1.json().get('branding_applied'):
            print("\n✅ Test 1 (No auth) worked with branding!")
            return True
        elif response2.status_code == 200 and response2.json().get('branding_applied'):
            print("\n✅ Test 2 (User ID header) worked with branding!")
            return True
        elif response3.status_code == 200 and response3.json().get('branding_applied'):
            print("\n✅ Test 3 (Clerk token) worked with branding!")
            return True
        else:
            print("\n❌ None of the authentication methods worked with branding")
            return False
        
    except Exception as e:
        print(f"❌ Error testing frontend auth: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the frontend authentication test."""
    print("🎯 Testing Frontend Authentication")
    print("=" * 50)
    
    # Test: Frontend Authentication
    print("\n1️⃣ Testing Frontend Authentication...")
    auth_success = test_frontend_auth()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY:")
    print(f"   Frontend Authentication: {'✅ PASS' if auth_success else '❌ FAIL'}")
    
    if auth_success:
        print("\n🎉 TEST PASSED!")
        print("✅ Frontend authentication is working with branding")
        print("✅ The API is correctly applying branding")
        print("✅ The issue might be in the frontend display")
        return True
    else:
        print("\n❌ TEST FAILED")
        print("❌ Frontend authentication is not working with branding")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
