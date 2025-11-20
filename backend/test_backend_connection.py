#!/usr/bin/env python
"""
Simple test to check if the backend is running and accessible
"""
import requests
import json

def test_backend_connection():
    """Test if the backend is running and accessible"""
    print("🧪 Testing Backend Connection...")
    
    try:
        # Test the main API status endpoint
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Backend is running (Status: {response.status_code})")
        
        # Test the branding kit status endpoint
        response = requests.get("http://127.0.0.1:8000/api/ai/branding-kit/status/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Branding Kit API is accessible: {result.get('message')}")
        else:
            print(f"❌ Branding Kit API not accessible (Status: {response.status_code})")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running or not accessible")
        print("   Make sure to start the Django backend server:")
        print("   cd backend && python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Error testing backend connection: {e}")
        return False

if __name__ == "__main__":
    success = test_backend_connection()
    exit(0 if success else 1)
