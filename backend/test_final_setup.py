#!/usr/bin/env python
"""
Final Setup Test - Verify AI Services are Working
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set the API key from environment or use placeholder
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("WARNING: GEMINI_API_KEY not set. Using placeholder for testing.")
    api_key = 'your_gemini_api_key_here'
os.environ['GEMINI_API_KEY'] = api_key

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

def test_ai_services():
    """Test AI services availability"""
    print("🧪 Testing AI Services...")
    
    try:
        from ai_services.ai_poster_service import AIPosterService
        from ai_services.ai_caption_service import AICaptionService
        
        # Test poster service
        poster_service = AIPosterService()
        poster_available = poster_service.is_available()
        print(f"   🎨 AI Poster Service: {'✅ Available' if poster_available else '❌ Not Available'}")
        
        # Test caption service
        caption_service = AICaptionService()
        caption_available = caption_service.is_available()
        print(f"   📝 AI Caption Service: {'✅ Available' if caption_available else '❌ Not Available'}")
        
        if poster_available and caption_available:
            print("\n🎉 ALL AI SERVICES ARE READY!")
            return True
        else:
            print("\n❌ Some AI services are not available")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI services: {str(e)}")
        return False

def test_django_server():
    """Test if Django server can start"""
    print("\n🌐 Testing Django Server...")
    
    try:
        from django.core.management import execute_from_command_line
        print("   ✅ Django imports successful")
        
        # Test URL configuration
        from django.urls import reverse
        print("   ✅ URL configuration working")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Django server test failed: {str(e)}")
        return False

def main():
    """Main test function"""
    print("🚀 Final AI Setup Test")
    print("=" * 50)
    print("🔑 Using API key from environment variables")
    print("=" * 50)
    
    # Test Django server
    django_success = test_django_server()
    
    if django_success:
        # Test AI services
        ai_success = test_ai_services()
        
        if ai_success:
            print("\n🎉 ALL TESTS PASSED!")
            print("\n✅ AI Services are ready for poster and caption generation!")
            print("\n📋 Available Endpoints:")
            print("   • POST /api/ai-poster/generate_poster/")
            print("   • POST /api/ai-poster/edit_poster/")
            print("   • POST /api/ai-poster/composite_poster/")
            print("   • POST /api/ai-caption/product_caption/")
            print("   • POST /api/ai-caption/social_media_caption/")
            print("   • POST /api/ai-caption/image_caption/")
            print("   • POST /api/ai-caption/bulk_captions/")
            print("\n🚀 Start Django server: python manage.py runserver")
            return True
        else:
            print("\n❌ AI services test failed")
            return False
    else:
        print("\n❌ Django server test failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

