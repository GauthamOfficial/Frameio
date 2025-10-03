#!/usr/bin/env python
"""
Setup script to create a test user and organization for development.
This helps resolve the "Organization not found or access denied" error.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from users.models import UserProfile

User = get_user_model()

def create_test_data():
    """Create test user and organization data."""
    
    # Create test organization
    org, created = Organization.objects.get_or_create(
        name="Test Organization",
        defaults={
            'domain': 'test.com',
            'description': 'Test organization for development'
        }
    )
    
    if created:
        print(f"✅ Created organization: {org.name}")
    else:
        print(f"✅ Found existing organization: {org.name}")
    
    # Create test user
    user, created = User.objects.get_or_create(
        email="test@example.com",
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Created user: {user.email}")
    else:
        print(f"✅ Found existing user: {user.email}")
    
    # Create user profile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'current_organization': org,
            'job_title': 'Test Admin',
            'department': 'Development',
            'company_size': '1-10'
        }
    )
    
    if created:
        print(f"✅ Created user profile for: {user.email}")
    else:
        print(f"✅ Found existing user profile for: {user.email}")
    
    # Create organization membership
    membership, created = OrganizationMember.objects.get_or_create(
        user=user,
        organization=org,
        defaults={
            'role': 'admin',
            'is_active': True,
            'can_invite_users': True,
            'can_manage_billing': True,
            'can_export_data': True
        }
    )
    
    if created:
        print(f"✅ Created organization membership: {user.email} -> {org.name}")
    else:
        print(f"✅ Found existing membership: {user.email} -> {org.name}")
    
    print("\n🎉 Test data setup complete!")
    print(f"Organization ID: {org.id}")
    print(f"User ID: {user.id}")
    print(f"User Email: {user.email}")
    print(f"User Role: {membership.role}")
    
    return org, user, profile

if __name__ == "__main__":
    try:
        org, user, profile = create_test_data()
        print("\n✅ Setup completed successfully!")
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        sys.exit(1)
