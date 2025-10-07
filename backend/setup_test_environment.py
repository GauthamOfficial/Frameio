#!/usr/bin/env python
"""
Setup script for test environment.
This script creates test users, organizations, and memberships for development and testing.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from users.mock_auth import MockAuthService
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember

User = get_user_model()


def setup_test_environment():
    """Set up complete test environment."""
    print("🚀 Setting up test environment...")
    
    try:
        # Create test data
        test_data = MockAuthService.setup_test_environment()
        
        user = test_data['user']
        organization = test_data['organization']
        membership = test_data['membership']
        
        print(f"✅ Created test user: {user.email}")
        print(f"✅ Created test organization: {organization.name}")
        print(f"✅ Created membership: {user.email} -> {organization.name} ({membership.role})")
        
        # Create additional test users for different roles
        manager_user = MockAuthService.create_test_user(
            email="manager@example.com",
            password="testpass123"
        )
        manager_user.first_name = "Manager"
        manager_user.last_name = "User"
        manager_user.save()
        
        MockAuthService.create_test_membership(
            manager_user, organization, role="manager"
        )
        print(f"✅ Created manager user: {manager_user.email}")
        
        designer_user = MockAuthService.create_test_user(
            email="designer@example.com",
            password="testpass123"
        )
        designer_user.first_name = "Designer"
        designer_user.last_name = "User"
        designer_user.save()
        
        MockAuthService.create_test_membership(
            designer_user, organization, role="designer"
        )
        print(f"✅ Created designer user: {designer_user.email}")
        
        # Create a second organization for multi-tenant testing
        org2 = MockAuthService.create_test_organization(
            name="Second Organization",
            slug="second-org"
        )
        
        MockAuthService.create_test_membership(
            user, org2, role="admin"
        )
        print(f"✅ Created second organization: {org2.name}")
        
        print("\n🎉 Test environment setup complete!")
        print("\nTest credentials:")
        print(f"Admin: admin@example.com / testpass123")
        print(f"Manager: manager@example.com / testpass123")
        print(f"Designer: designer@example.com / testpass123")
        print(f"\nOrganization IDs:")
        print(f"Primary: {organization.id}")
        print(f"Secondary: {org2.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up test environment: {e}")
        return False


def cleanup_test_environment():
    """Clean up test environment."""
    print("🧹 Cleaning up test environment...")
    
    try:
        # Delete test users
        test_emails = [
            "test@example.com",
            "manager@example.com", 
            "designer@example.com"
        ]
        
        for email in test_emails:
            try:
                user = User.objects.get(email=email)
                user.delete()
                print(f"✅ Deleted user: {email}")
            except User.DoesNotExist:
                pass
        
        # Delete test organizations
        test_slugs = ["test-org", "second-org"]
        for slug in test_slugs:
            try:
                org = Organization.objects.get(slug=slug)
                org.delete()
                print(f"✅ Deleted organization: {slug}")
            except Organization.DoesNotExist:
                pass
        
        print("🎉 Test environment cleanup complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up test environment: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cleanup":
        cleanup_test_environment()
    else:
        setup_test_environment()
