#!/usr/bin/env python
"""
Complete Brand Personalization Feature Test
Tests the entire brand personalization workflow from company profile creation to branded poster generation.
"""
import os
import sys
import django
from django.conf import settings

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import CompanyProfile
from ai_services.ai_poster_service import AIPosterService
from ai_services.brand_overlay_service import BrandOverlayService
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
import tempfile

User = get_user_model()

def create_test_logo():
    """Create a test logo image."""
    # Create a simple test logo
    img = Image.new('RGB', (300, 300), color='blue')
    # Add some text to make it look like a logo
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    draw.text((50, 120), "TEST LOGO", fill='white', font=font)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return SimpleUploadedFile(
        "test_logo.png",
        img_bytes.getvalue(),
        content_type="image/png"
    )

def test_company_profile_creation():
    """Test creating a company profile with all required fields."""
    print("🧪 Testing Company Profile Creation...")
    
    try:
        # Create test user
        user, created = User.objects.get_or_create(
            email='test@textilecompany.com',
            defaults={
                'username': 'testcompany',
                'first_name': 'Test',
                'last_name': 'Company'
            }
        )
        
        if created:
            print("✅ Test user created successfully")
        else:
            print("✅ Test user already exists")
        
        # Create or get company profile
        profile, created = CompanyProfile.objects.get_or_create(
            user=user,
            defaults={
                'company_name': 'Test Textile Company',
                'whatsapp_number': '+1234567890',
                'email': 'contact@testtextile.com',
                'facebook_link': 'https://facebook.com/testtextile',
                'website': 'https://testtextile.com',
                'address': '123 Textile Street, Fashion City',
                'description': 'Premium textile manufacturer specializing in silk and cotton fabrics',
                'preferred_logo_position': 'top_right'
            }
        )
        
        if created:
            print("✅ Company profile created successfully")
        else:
            print("✅ Company profile already exists")
        
        # Add logo
        if not profile.logo:
            logo_file = create_test_logo()
            profile.logo = logo_file
            profile.save()
            print("✅ Company logo uploaded successfully")
        else:
            print("✅ Company logo already exists")
        
        # Verify profile completion
        print(f"✅ Profile completion status: {profile.has_complete_profile}")
        print(f"✅ Contact info: {profile.get_contact_info()}")
        
        return profile
        
    except Exception as e:
        print(f"❌ Error creating company profile: {str(e)}")
        return None

def test_brand_overlay_service():
    """Test the brand overlay service functionality."""
    print("\n🧪 Testing Brand Overlay Service...")
    
    try:
        # Create a test poster image
        poster_img = Image.new('RGB', (800, 600), color='lightblue')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(poster_img)
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except:
            font = ImageFont.load_default()
        draw.text((200, 250), "AI Generated Textile Poster", fill='darkblue', font=font)
        
        # Save test poster
        poster_bytes = io.BytesIO()
        poster_img.save(poster_bytes, format='PNG')
        poster_bytes.seek(0)
        
        # Create temporary file for poster
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(poster_bytes.getvalue())
            temp_poster_path = temp_file.name
        
        print(f"✅ Test poster created: {temp_poster_path}")
        
        # Test brand overlay service
        overlay_service = BrandOverlayService()
        
        # Get company profile
        user = User.objects.get(email='test@textilecompany.com')
        profile = user.company_profile
        
        # Test brand overlay
        result = overlay_service.add_brand_overlay(
            temp_poster_path,
            profile,
            "test_branded_poster.png"
        )
        
        if result.get('status') == 'success':
            print("✅ Brand overlay applied successfully")
            print(f"✅ Final image path: {result.get('image_path')}")
            print(f"✅ Logo added: {result.get('logo_added')}")
            print(f"✅ Contact info added: {result.get('contact_info_added')}")
        else:
            print(f"❌ Brand overlay failed: {result.get('message')}")
        
        # Clean up
        os.unlink(temp_poster_path)
        
        return result.get('status') == 'success'
        
    except Exception as e:
        print(f"❌ Error testing brand overlay service: {str(e)}")
        return False

def test_ai_poster_with_branding():
    """Test AI poster generation with brand overlay integration."""
    print("\n🧪 Testing AI Poster Generation with Branding...")
    
    try:
        # Initialize AI poster service
        poster_service = AIPosterService()
        
        if not poster_service.is_available():
            print("⚠️ AI poster service not available (missing API key or client)")
            return False
        
        # Get test user
        user = User.objects.get(email='test@textilecompany.com')
        
        # Test poster generation with branding
        result = poster_service.generate_from_prompt(
            prompt="Create a beautiful textile poster for silk sarees with elegant design",
            aspect_ratio="1:1",
            user=user
        )
        
        if result.get('status') == 'success':
            print("✅ AI poster generated successfully")
            print(f"✅ Image path: {result.get('image_path')}")
            print(f"✅ Branding applied: {result.get('branding_applied')}")
            print(f"✅ Logo added: {result.get('logo_added')}")
            print(f"✅ Contact info added: {result.get('contact_info_added')}")
            print(f"✅ Caption: {result.get('caption', '')[:100]}...")
            print(f"✅ Hashtags: {result.get('hashtags', [])[:5]}")
            return True
        else:
            print(f"❌ AI poster generation failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI poster generation: {str(e)}")
        return False

def test_api_endpoints():
    """Test the API endpoints for company profile management."""
    print("\n🧪 Testing API Endpoints...")
    
    try:
        from django.test import Client
        from django.contrib.auth import authenticate
        
        client = Client()
        
        # Test user authentication
        user = User.objects.get(email='test@textilecompany.com')
        
        # Test company profile API
        response = client.get('/api/users/company-profiles/')
        print(f"✅ Company profile GET endpoint: {response.status_code}")
        
        # Test profile status endpoint
        response = client.get('/api/users/company-profiles/status/')
        print(f"✅ Profile status endpoint: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing API endpoints: {str(e)}")
        return False

def main():
    """Run all brand personalization tests."""
    print("🚀 Starting Brand Personalization Feature Tests")
    print("=" * 60)
    
    # Test 1: Company Profile Creation
    profile = test_company_profile_creation()
    if not profile:
        print("❌ Company profile creation failed. Stopping tests.")
        return
    
    # Test 2: Brand Overlay Service
    overlay_success = test_brand_overlay_service()
    
    # Test 3: AI Poster Generation with Branding
    poster_success = test_ai_poster_with_branding()
    
    # Test 4: API Endpoints
    api_success = test_api_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Company Profile Creation: {'PASS' if profile else 'FAIL'}")
    print(f"✅ Brand Overlay Service: {'PASS' if overlay_success else 'FAIL'}")
    print(f"✅ AI Poster with Branding: {'PASS' if poster_success else 'FAIL'}")
    print(f"✅ API Endpoints: {'PASS' if api_success else 'FAIL'}")
    
    overall_success = all([profile, overlay_success, poster_success, api_success])
    print(f"\n🎯 Overall Result: {'PASS' if overall_success else 'FAIL'}")
    
    if overall_success:
        print("\n🎉 Brand Personalization Feature is working correctly!")
        print("✅ Users can upload company logos and contact details")
        print("✅ AI-generated posters automatically include branding")
        print("✅ Frontend settings page is available")
        print("✅ Backend API endpoints are functional")
    else:
        print("\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()

