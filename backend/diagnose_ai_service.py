#!/usr/bin/env python3
"""
Comprehensive AI Service Diagnostic Tool
Run this from the backend directory: python diagnose_ai_service.py
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.ai_poster_service import AIPosterService

def diagnose_ai_service():
    print("🔍 AI Service Diagnostic Tool\n")
    
    # Check 1: Environment Variables
    print("1. Checking Environment Variables...")
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"   ✅ GEMINI_API_KEY found: {api_key[:10]}...")
        print(f"   📏 Key length: {len(api_key)} characters")
    else:
        print("   ❌ GEMINI_API_KEY not found")
        print("   💡 Set GEMINI_API_KEY in your environment or .env file")
        return False
    
    # Check 2: Python Dependencies
    print("\n2. Checking Python Dependencies...")
    try:
        from google import genai
        print("   ✅ google-genai is installed")
    except ImportError:
        print("   ❌ google-genai not installed")
        print("   💡 Install with: pip install google-genai")
        return False
    
    try:
        from PIL import Image
        print("   ✅ Pillow (PIL) is installed")
    except ImportError:
        print("   ❌ Pillow not installed")
        print("   💡 Install with: pip install Pillow")
        return False
    
    # Check 3: Django Settings
    print("\n3. Checking Django Settings...")
    try:
        from django.conf import settings
        print(f"   ✅ Django settings loaded")
        print(f"   📁 Media root: {getattr(settings, 'MEDIA_ROOT', 'Not set')}")
        print(f"   🌐 Media URL: {getattr(settings, 'MEDIA_URL', 'Not set')}")
    except Exception as e:
        print(f"   ❌ Django settings error: {e}")
        return False
    
    # Check 4: AI Service Initialization
    print("\n4. Testing AI Service Initialization...")
    try:
        service = AIPosterService()
        print("   ✅ AI Poster Service created")
        
        # Check if service is available
        is_available = service.is_available()
        print(f"   📊 Service available: {is_available}")
        
        if not is_available:
            print("   ❌ Service is not available")
            if not service.api_key:
                print("   🔍 Issue: No API key found")
            if not service.client:
                print("   🔍 Issue: No client initialized")
        else:
            print("   ✅ Service is available and ready")
            
    except Exception as e:
        print(f"   ❌ AI Service initialization failed: {e}")
        return False
    
    # Check 5: Test API Connection
    if is_available:
        print("\n5. Testing API Connection...")
        try:
            # Test a simple generation
            result = service.generate_from_prompt(
                "A simple test image for diagnostic purposes",
                "1:1"
            )
            
            if result.get('status') == 'success':
                print("   ✅ Image generation successful")
                print(f"   📁 Image path: {result.get('image_path', 'N/A')}")
                print(f"   🌐 Image URL: {result.get('image_url', 'N/A')}")
            else:
                print(f"   ❌ Image generation failed: {result.get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"   ❌ API connection test failed: {e}")
            return False
    
    print("\n🎉 AI Service is working correctly!")
    return True

def show_fix_instructions():
    print("\n🔧 Fix Instructions:")
    print("=" * 50)
    print("1. Set GEMINI_API_KEY environment variable:")
    print("   export GEMINI_API_KEY='your_actual_api_key_here'")
    print("   # Or add to .env file:")
    print("   echo 'GEMINI_API_KEY=your_actual_api_key_here' >> .env")
    print()
    print("2. Install required Python packages:")
    print("   pip install google-genai Pillow")
    print()
    print("3. Restart your Django server:")
    print("   python manage.py runserver")
    print()
    print("4. Get your Gemini API key from:")
    print("   https://aistudio.google.com/app/apikey")

if __name__ == "__main__":
    print("🚀 Starting AI Service Diagnostic...\n")
    
    success = diagnose_ai_service()
    
    if not success:
        print("\n❌ AI Service is not working properly")
        show_fix_instructions()
        sys.exit(1)
    else:
        print("\n✅ AI Service is ready to use!")
        print("🎯 You can now generate images through the frontend")


