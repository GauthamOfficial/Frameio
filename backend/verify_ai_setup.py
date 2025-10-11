#!/usr/bin/env python
"""
AI Services Setup Verification Script
Verify that all AI services are ready for poster and caption generation
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the API key before Django setup
os.environ['GEMINI_API_KEY'] = 'AIzaSyCZiGdU4pk_-uVNWCquY5C15vaxnPszA-s'

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def verify_dependencies():
    """Verify all required dependencies are installed"""
    print("🔍 Checking Dependencies...")
    
    required_packages = [
        'google.genai',
        'PIL',
        'django',
        'rest_framework'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'google.genai':
                import google.genai
                print(f"   ✅ {package} - Available")
            elif package == 'PIL':
                from PIL import Image
                print(f"   ✅ {package} - Available")
            elif package == 'django':
                import django
                print(f"   ✅ {package} - Available")
            elif package == 'rest_framework':
                import rest_framework
                print(f"   ✅ {package} - Available")
        except ImportError:
            missing_packages.append(package)
            print(f"   ❌ {package} - Missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("   ✅ All dependencies available")
    return True

def verify_api_key():
    """Verify Google API key is configured"""
    print("\n🔑 Checking API Key Configuration...")
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("   ❌ GEMINI_API_KEY not found in environment")
        print("   Add to your .env file: GEMINI_API_KEY=your_key_here")
        return False
    
    if api_key == "your_gemini_api_key_here" or len(api_key) < 20:
        print("   ❌ GEMINI_API_KEY appears to be placeholder")
        print("   Get your real API key from: https://aistudio.google.com/app/apikey")
        return False
    
    print(f"   ✅ GEMINI_API_KEY configured (length: {len(api_key)})")
    return True

def verify_services():
    """Verify AI services can be initialized"""
    print("\n🤖 Checking AI Services...")
    
    try:
        from ai_services.ai_poster_service import AIPosterService
        from ai_services.ai_caption_service import AICaptionService
        
        # Test poster service
        poster_service = AIPosterService()
        if poster_service.is_available():
            print("   ✅ AI Poster Service - Ready")
        else:
            print("   ❌ AI Poster Service - Not available")
            return False
        
        # Test caption service
        caption_service = AICaptionService()
        if caption_service.is_available():
            print("   ✅ AI Caption Service - Ready")
        else:
            print("   ❌ AI Caption Service - Not available")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error initializing services: {str(e)}")
        return False

def verify_urls():
    """Verify URL routing is configured"""
    print("\n🌐 Checking URL Configuration...")
    
    try:
        from ai_services.urls import urlpatterns
        
        # Check for AI poster URLs
        poster_urls = [url for url in urlpatterns if 'ai-poster' in str(url.pattern)]
        if len(poster_urls) >= 4:
            print(f"   ✅ AI Poster URLs - {len(poster_urls)} endpoints")
        else:
            print("   ❌ AI Poster URLs - Missing endpoints")
            return False
        
        # Check for AI caption URLs
        caption_urls = [url for url in urlpatterns if 'ai-caption' in str(url.pattern)]
        if len(caption_urls) >= 5:
            print(f"   ✅ AI Caption URLs - {len(caption_urls)} endpoints")
        else:
            print("   ❌ AI Caption URLs - Missing endpoints")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking URLs: {str(e)}")
        return False

def verify_media_storage():
    """Verify media storage is configured"""
    print("\n💾 Checking Media Storage...")
    
    try:
        from django.core.files.storage import default_storage
        from django.conf import settings
        
        if hasattr(settings, 'MEDIA_ROOT'):
            print("   ✅ Media storage configured")
            return True
        else:
            print("   ❌ Media storage not configured")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking media storage: {str(e)}")
        return False

def main():
    """Main verification function"""
    print("🚀 AI Services Setup Verification")
    print("=" * 50)
    
    checks = [
        ("Dependencies", verify_dependencies),
        ("API Key", verify_api_key),
        ("AI Services", verify_services),
        ("URL Routing", verify_urls),
        ("Media Storage", verify_media_storage)
    ]
    
    all_passed = True
    
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"   ❌ {check_name} check failed: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("\n✅ AI Services are ready for poster and caption generation!")
        print("\n📋 Available Endpoints:")
        print("   • POST /api/ai-poster/generate_poster/")
        print("   • POST /api/ai-poster/edit_poster/")
        print("   • POST /api/ai-poster/composite_poster/")
        print("   • POST /api/ai-caption/product_caption/")
        print("   • POST /api/ai-caption/social_media_caption/")
        print("   • POST /api/ai-caption/image_caption/")
        print("   • POST /api/ai-caption/bulk_captions/")
        print("\n🚀 Start generating AI content!")
        return True
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🔧 Fix the issues above and run this script again.")
        print("\n📖 Setup Guide:")
        print("   1. Get API key: https://aistudio.google.com/app/apikey")
        print("   2. Add to .env: GOOGLE_API_KEY=your_key_here")
        print("   3. Install deps: pip install -r requirements.txt")
        print("   4. Run this script again")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
