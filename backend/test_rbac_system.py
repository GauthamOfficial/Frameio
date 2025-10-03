#!/usr/bin/env python
"""
Test script for RBAC (Role-Based Access Control) system.
This script creates test users with different roles and verifies access permissions.
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
from organizations.models import Organization, OrganizationMember
from users.roles import get_user_role_permissions, check_api_permission
from users.permissions import get_user_organization_permissions
import uuid

User = get_user_model()

def create_test_organization():
    """Create a test organization."""
    org, created = Organization.objects.get_or_create(
        slug='test-org-rbac',
        defaults={
            'name': 'Test RBAC Organization',
            'description': 'Organization for testing RBAC system',
            'subscription_plan': 'premium',
            'subscription_status': 'active'
        }
    )
    return org

def create_test_users():
    """Create test users with different roles."""
    users = {}
    
    # Create Admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@test.com',
        defaults={
            'username': 'admin_test',
            'first_name': 'Admin',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True
        }
    )
    users['admin'] = admin_user
    
    # Create Manager user
    manager_user, created = User.objects.get_or_create(
        email='manager@test.com',
        defaults={
            'username': 'manager_test',
            'first_name': 'Manager',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True
        }
    )
    users['manager'] = manager_user
    
    # Create Designer user
    designer_user, created = User.objects.get_or_create(
        email='designer@test.com',
        defaults={
            'username': 'designer_test',
            'first_name': 'Designer',
            'last_name': 'User',
            'is_active': True,
            'is_verified': True
        }
    )
    users['designer'] = designer_user
    
    return users

def create_organization_memberships(org, users):
    """Create organization memberships for test users."""
    memberships = {}
    
    # Admin membership
    admin_membership, created = OrganizationMember.objects.get_or_create(
        user=users['admin'],
        organization=org,
        defaults={
            'role': 'admin',
            'is_active': True,
            'can_invite_users': True,
            'can_manage_billing': True,
            'can_export_data': True
        }
    )
    memberships['admin'] = admin_membership
    
    # Manager membership
    manager_membership, created = OrganizationMember.objects.get_or_create(
        user=users['manager'],
        organization=org,
        defaults={
            'role': 'manager',
            'is_active': True,
            'can_invite_users': True,
            'can_manage_billing': False,
            'can_export_data': True
        }
    )
    memberships['manager'] = manager_membership
    
    # Designer membership
    designer_membership, created = OrganizationMember.objects.get_or_create(
        user=users['designer'],
        organization=org,
        defaults={
            'role': 'designer',
            'is_active': True,
            'can_invite_users': False,
            'can_manage_billing': False,
            'can_export_data': False
        }
    )
    memberships['designer'] = designer_membership
    
    return memberships

def test_role_permissions():
    """Test role-based permissions."""
    print("=" * 60)
    print("TESTING RBAC SYSTEM")
    print("=" * 60)
    
    # Create test data
    org = create_test_organization()
    users = create_test_users()
    memberships = create_organization_memberships(org, users)
    
    print(f"Created test organization: {org.name}")
    print(f"Created test users: {len(users)}")
    print()
    
    # Test permissions for each role
    roles_to_test = ['admin', 'manager', 'designer']
    
    for role in roles_to_test:
        user = users[role]
        print(f"Testing {role.upper()} role permissions:")
        print("-" * 40)
        
        # Get role permissions
        permissions = get_user_role_permissions(user, org)
        if permissions:
            print(f"Role: {permissions['role']}")
            print(f"Can manage users: {permissions['can_manage_users']}")
            print(f"Can manage billing: {permissions['can_manage_billing']}")
            print(f"Can export data: {permissions['can_export_data']}")
            print(f"Can access analytics: {permissions['can_access_analytics']}")
            print(f"Can manage AI services: {permissions['can_manage_ai_services']}")
            print(f"Can generate AI: {permissions['can_generate_ai']}")
            print(f"Can approve designs: {permissions['can_approve_designs']}")
            print(f"Can manage projects: {permissions['can_manage_projects']}")
        else:
            print(f"ERROR: No permissions found for {role}")
        
        print()
    
    # Test API permissions
    print("Testing API permissions:")
    print("-" * 40)
    
    api_endpoints = [
        '/api/users/',
        '/api/users/invite_user/',
        '/api/ai/generation-requests/',
        '/api/ai/analytics/',
        '/api/ai/quotas/',
    ]
    
    for endpoint in api_endpoints:
        print(f"\nEndpoint: {endpoint}")
        for role in roles_to_test:
            user = users[role]
            has_access = check_api_permission(user, org, endpoint)
            print(f"  {role}: {'✓' if has_access else '✗'}")
    
    print()
    
    # Test backward compatibility
    print("Testing backward compatibility:")
    print("-" * 40)
    
    for role in roles_to_test:
        user = users[role]
        old_permissions = get_user_organization_permissions(user, org)
        new_permissions = get_user_role_permissions(user, org)
        
        print(f"{role}:")
        print(f"  Old system: {old_permissions['role'] if old_permissions else 'None'}")
        print(f"  New system: {new_permissions['role'] if new_permissions else 'None'}")
        print(f"  Match: {'✓' if old_permissions and new_permissions and old_permissions['role'] == new_permissions['role'] else '✗'}")
    
    print()
    print("RBAC system test completed!")
    print("=" * 60)

def test_middleware_integration():
    """Test middleware integration with role context."""
    print("\nTesting middleware integration:")
    print("-" * 40)
    
    # This would typically be tested with actual HTTP requests
    # For now, we'll simulate the middleware behavior
    
    org = Organization.objects.get(slug='test-org-rbac')
    users = create_test_users()
    
    for role in ['admin', 'manager', 'designer']:
        user = users[role]
        membership = OrganizationMember.objects.get(
            user=user,
            organization=org,
            is_active=True
        )
        
        # Simulate middleware setting role context
        role_context = {
            'role': membership.role,
            'organization_membership': membership,
            'role_permissions': get_user_role_permissions(user, org)
        }
        
        print(f"{role}: {role_context['role']} with {len(role_context['role_permissions'])} permissions")

if __name__ == '__main__':
    try:
        test_role_permissions()
        test_middleware_integration()
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
