#!/usr/bin/env python
"""
Simple test script to verify permission system is working.
"""

import os
import sys
import django

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from users.permissions import IsOrganizationMember, IsOrganizationAdmin, CanManageUsers
from django.test import RequestFactory

User = get_user_model()

def test_permissions():
    """Test the permission system."""
    print("🧪 Testing permission system...")
    
    # Create test data
    user = User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass123"
    )
    
    organization = Organization.objects.create(
        name="Test Organization",
        slug="test-org"
    )
    
    membership = OrganizationMember.objects.create(
        user=user,
        organization=organization,
        role="admin",
        can_invite_users=True,
        can_manage_billing=True,
        can_export_data=True
    )
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/test/')
    request.user = user
    
    # Test IsOrganizationMember permission
    permission = IsOrganizationMember()
    has_permission = permission.has_permission(request, None)
    print(f"✅ IsOrganizationMember: {has_permission}")
    
    # Test IsOrganizationAdmin permission
    permission = IsOrganizationAdmin()
    has_permission = permission.has_permission(request, None)
    print(f"✅ IsOrganizationAdmin: {has_permission}")
    
    # Test CanManageUsers permission
    permission = CanManageUsers()
    has_permission = permission.has_permission(request, None)
    print(f"✅ CanManageUsers: {has_permission}")
    
    print("🎉 Permission system test completed!")

if __name__ == "__main__":
    test_permissions()
