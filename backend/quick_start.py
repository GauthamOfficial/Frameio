#!/usr/bin/env python
"""
Quick start script for Phase 1 Week 3 testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from ai_services.models import AIProvider

User = get_user_model()

def quick_setup():
    """Quick setup for testing"""
    print("🚀 Quick Setup for Phase 1 Week 3 Testing")
    print("=" * 50)
    
    # Create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("✅ Created test user: testuser / testpass123")
    else:
        print("✅ Test user already exists: testuser / testpass123")
    
    # Create test organization
    org, created = Organization.objects.get_or_create(
        slug='test-org',
        defaults={
            'name': 'Test Organization',
            'description': 'Test organization for Phase 1 Week 3'
        }
    )
    if created:
        print("✅ Created test organization: Test Organization")
    else:
        print("✅ Test organization already exists")
    
    # Create membership
    membership, created = OrganizationMember.objects.get_or_create(
        organization=org,
        user=user,
        defaults={'role': 'admin'}
    )
    if created:
        print("✅ Created organization membership")
    else:
        print("✅ Organization membership already exists")
    
    # Create AI provider
    provider, created = AIProvider.objects.get_or_create(
        name='nanobanana',
        defaults={
            'is_active': True,
            'rate_limit_per_minute': 60,
            'rate_limit_per_hour': 1000
        }
    )
    if created:
        print("✅ Created AI provider: nanobanana")
    else:
        print("✅ AI provider already exists")
    
    print("\n🎉 Setup Complete!")
    print("\n📋 Test Credentials:")
    print("  Username: testuser")
    print("  Password: testpass123")
    print("  Organization: test-org")
    
    print("\n🌐 Start the server:")
    print("  python manage.py runserver")
    
    print("\n🔧 Test the endpoints:")
    print("  Open: http://localhost:8000/simple_test_interface.html")
    
    return True

if __name__ == '__main__':
    quick_setup()
