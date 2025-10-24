#!/usr/bin/env python
"""
Test script for Branding Kit API endpoints
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.branding_kit_service import BrandingKitService

def test_branding_kit_service():
    """Test the branding kit service"""
    print("🧪 Testing Branding Kit Service...")
    
    # Initialize service
    service = BrandingKitService()
    
    # Check if service is available
    if not service.is_available():
        print("❌ Branding Kit service not available")
        print("   Make sure GEMINI_API_KEY is set in environment variables")
        return False
    
    print("✅ Branding Kit service is available")
    
    # Test logo generation
    print("\n🎨 Testing logo generation...")
    logo_result = service.generate_logo("Modern tech startup logo with clean lines", "modern")
    
    if logo_result.get('success'):
        print("✅ Logo generation successful")
        print(f"   Format: {logo_result['logo']['format']}")
        print(f"   Size: {logo_result['logo']['width']}x{logo_result['logo']['height']}")
    else:
        print(f"❌ Logo generation failed: {logo_result.get('error')}")
        return False
    
    # Test color palette generation
    print("\n🎨 Testing color palette generation...")
    palette_result = service.generate_color_palette("Modern tech startup", 5)
    
    if palette_result.get('success'):
        print("✅ Color palette generation successful")
        print(f"   Format: {palette_result['palette']['format']}")
        print(f"   Size: {palette_result['palette']['width']}x{palette_result['palette']['height']}")
    else:
        print(f"❌ Color palette generation failed: {palette_result.get('error')}")
        return False
    
    # Test complete branding kit generation
    print("\n🎨 Testing complete branding kit generation...")
    kit_result = service.generate_branding_kit("Modern tech startup with clean aesthetic", "modern")
    
    if kit_result.get('success'):
        print("✅ Complete branding kit generation successful")
        branding_kit = kit_result['branding_kit']
        print(f"   Logo: {branding_kit['logo']['format']} ({branding_kit['logo']['width']}x{branding_kit['logo']['height']})")
        print(f"   Palette: {branding_kit['color_palette']['format']} ({branding_kit['color_palette']['width']}x{branding_kit['color_palette']['height']})")
    else:
        print(f"❌ Complete branding kit generation failed: {kit_result.get('error')}")
        return False
    
    print("\n🎉 All tests passed! Branding Kit service is working correctly.")
    return True

if __name__ == "__main__":
    success = test_branding_kit_service()
    sys.exit(0 if success else 1)
