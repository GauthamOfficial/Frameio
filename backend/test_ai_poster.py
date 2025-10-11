#!/usr/bin/env python
"""
Test script for AI Poster Generation Service
Run this to verify the Gemini 2.5 Flash integration is working
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

from ai_services.ai_poster_service import AIPosterService

def test_ai_poster_service():
    """Test the AI poster service"""
    print("🧪 Testing AI Poster Service...")
    
    # Initialize service
    service = AIPosterService()
    
    # Check if service is available
    if not service.is_available():
        print("❌ AI Poster Service is not available")
        print("   Make sure GOOGLE_API_KEY is set in your .env file")
        return False
    
    print("✅ AI Poster Service is available")
    
    # Test prompt generation
    test_prompt = "Create a modern textile poster for a silk saree brand. Include elegant typography and deep red tones."
    
    print(f"🎨 Testing poster generation with prompt: {test_prompt[:50]}...")
    
    result = service.generate_from_prompt(test_prompt, "4:5")
    
    if result.get('status') == 'success':
        print("✅ Poster generated successfully!")
        print(f"   Image path: {result.get('image_path')}")
        print(f"   Image URL: {result.get('image_url')}")
        return True
    else:
        print(f"❌ Poster generation failed: {result.get('message')}")
        return False

if __name__ == "__main__":
    print("🚀 AI Poster Generation Test")
    print("=" * 50)
    
    success = test_ai_poster_service()
    
    if success:
        print("\n🎉 All tests passed! AI Poster Service is ready.")
    else:
        print("\n💥 Tests failed. Check your configuration.")
        sys.exit(1)
