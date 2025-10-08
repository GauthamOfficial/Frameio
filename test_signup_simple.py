#!/usr/bin/env python3
"""
Simple test to verify signup functionality is working
"""
import requests
import time

def test_basic_connectivity():
    """Test basic connectivity to both servers"""
    print("🧪 Testing Basic Connectivity")
    print("=" * 40)
    
    # Test backend
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Backend: {response.status_code}")
    except Exception as e:
        print(f"❌ Backend: {e}")
    
    # Test frontend
    try:
        response = requests.get("http://localhost:3000/", timeout=5)
        print(f"✅ Frontend: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend: {e}")
    
    # Test signup page specifically
    try:
        response = requests.get("http://localhost:3000/sign-up", timeout=5)
        print(f"✅ Signup page: {response.status_code}")
        if response.status_code == 200:
            print("🎉 Signup page is working!")
            return True
    except Exception as e:
        print(f"❌ Signup page: {e}")
    
    return False

if __name__ == "__main__":
    test_basic_connectivity()
