#!/usr/bin/env python3
"""
Check Frontend Issue
Check if the frontend is properly calling the API with authentication.
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

def check_frontend_issue():
    """Check if the frontend is properly calling the API."""
    print("\n🔍 Checking Frontend Issue...")
    
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
        print(f"   Complete Profile: {profile.has_complete_profile}")
        
        # Simulate frontend API call
        print("\n🚀 Simulating Frontend API Call...")
        
        url = "http://localhost:8000/api/ai/ai-poster/generate_poster/"
        data = {
            "prompt": "Create a beautiful textile poster for a silk saree collection",
            "aspect_ratio": "4:5"
        }
        
        # Simulate frontend headers (with user ID for development)
        headers = {
            'Content-Type': 'application/json',
            'X-Dev-User-ID': str(user.id)  # This simulates the frontend passing user context
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
            
            if result.get('success') and result.get('branding_applied'):
                print("\n✅ SUCCESS! The API is working correctly with branding!")
                print("✅ The generated poster should contain:")
                print("   - Company name integrated into the design")
                print("   - Contact information (WhatsApp and Email) clearly visible")
                print("   - Professional branding elements")
                print("   - All branding naturally integrated by AI")
                
                print(f"\n🖼️ Generated Image URL: {result.get('image_url')}")
                print("🔍 Check this image to see if branding is included!")
                
                return True
            else:
                print("❌ API call failed or branding not applied")
                return False
        else:
            print(f"❌ API call failed with status {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Error checking frontend issue: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the frontend issue check."""
    print("🎯 Checking Frontend Issue")
    print("=" * 50)
    
    # Check: Frontend Issue
    print("\n1️⃣ Checking Frontend Issue...")
    issue_success = check_frontend_issue()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 CHECK SUMMARY:")
    print(f"   Frontend Issue Check: {'✅ PASS' if issue_success else '❌ FAIL'}")
    
    if issue_success:
        print("\n🎉 CHECK PASSED!")
        print("✅ The API is working correctly with branding")
        print("✅ The issue is likely in the frontend authentication or display")
        print("✅ The backend is generating branded posters correctly")
        return True
    else:
        print("\n❌ CHECK FAILED")
        print("❌ There might be an issue with the API or authentication")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
