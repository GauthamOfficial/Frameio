#!/usr/bin/env python
"""
Setup script to prepare the system for testing Phase 1 Week 3 features
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from ai_services.models import AIProvider

User = get_user_model()

def create_test_data():
    """Create test data for testing"""
    print("\n🔧 Creating test data...")
    
    # Create test user
    try:
        user = User.objects.get(username='testuser')
        print("✅ Test user already exists")
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print("✅ Test user created")
    
    # Create test organization
    try:
        org = Organization.objects.get(slug='test-org')
        print("✅ Test organization already exists")
    except Organization.DoesNotExist:
        org = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization for Phase 1 Week 3'
        )
        print("✅ Test organization created")
    
    # Create organization membership
    try:
        membership = OrganizationMember.objects.get(
            organization=org,
            user=user
        )
        print("✅ Organization membership already exists")
    except OrganizationMember.DoesNotExist:
        membership = OrganizationMember.objects.create(
            organization=org,
            user=user,
            role='admin'
        )
        print("✅ Organization membership created")
    
    # Create AI provider
    try:
        provider = AIProvider.objects.get(name='nanobanana')
        print("✅ AI provider already exists")
    except AIProvider.DoesNotExist:
        provider = AIProvider.objects.create(
            name='nanobanana',
            is_active=True,
            rate_limit_per_minute=60,
            rate_limit_per_hour=1000
        )
        print("✅ AI provider created")
    
    return user, org, provider

def print_test_instructions():
    """Print instructions for testing"""
    print("\n" + "=" * 70)
    print("🚀 PHASE 1 WEEK 3 - READY FOR TESTING!")
    print("=" * 70)
    
    print("\n📋 Test Data Created:")
    print("  👤 Username: testuser")
    print("  🔑 Password: testpass123")
    print("  🏢 Organization: Test Organization (test-org)")
    print("  🤖 AI Provider: nanobanana")
    
    print("\n🌐 Available Endpoints:")
    print("  🎨 POST /api/ai/textile/poster/generate_poster/")
    print("  📝 POST /api/ai/textile/caption/generate_caption/")
    print("  📅 POST /api/ai/schedule/")
    print("  📊 GET /api/ai/schedule/analytics/")
    print("  🔧 GET /api/ai/providers/")
    
    print("\n🔧 How to Test:")
    print("  1. Start the server: python manage.py runserver")
    print("  2. Open: http://localhost:8000/simple_test_interface.html")
    print("  3. Or use API tools like Postman/curl")
    print("  4. Include authentication headers:")
    print("     - Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=")
    print("     - X-Organization: test-org")
    
    print("\n📝 Example API Call:")
    print("""
curl -X POST http://localhost:8000/api/ai/textile/poster/generate_poster/ \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=" \\
  -H "X-Organization: test-org" \\
  -d '{
    "product_image_url": "https://example.com/product.jpg",
    "fabric_type": "saree",
    "festival": "deepavali",
    "price_range": "₹2999",
    "style": "elegant"
  }'
    """)
    
    print("\n🎯 What You Can Test:")
    print("  ✅ AI-powered textile poster generation")
    print("  ✅ AI caption and hashtag generation")
    print("  ✅ Social media post scheduling")
    print("  ✅ Usage limit enforcement")
    print("  ✅ Multi-tenant organization support")
    print("  ✅ Complete workflow integration")
    
    print("\n" + "=" * 70)

def main():
    """Main setup function"""
    print("🚀 Setting up Phase 1 Week 3 for testing...")
    
    try:
        user, org, provider = create_test_data()
        print_test_instructions()
        
        print("\n🎉 Setup complete! You can now test all Phase 1 Week 3 features.")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
