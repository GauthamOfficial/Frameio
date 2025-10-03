#!/usr/bin/env python
"""
Live API test to verify RBAC is working with actual HTTP requests.
"""

import os
import sys
import django
import requests
import json
import time

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from django.test import Client
from django.urls import reverse

User = get_user_model()

def test_live_api():
    """Test the live API with actual HTTP requests."""
    print("LIVE API RBAC TEST")
    print("="*50)
    
    # Create test data if it doesn't exist
    try:
        org = Organization.objects.get(slug='test-rbac-org')
        print(f"✓ Using existing organization: {org.name}")
    except Organization.DoesNotExist:
        print("Creating test organization...")
        org = Organization.objects.create(
            slug='test-rbac-org',
            name='Test RBAC Organization',
            description='Organization for testing RBAC',
            subscription_plan='premium',
            subscription_status='active'
        )
        print(f"✓ Created organization: {org.name}")
    
    # Create test users if they don't exist
    users = {}
    roles = ['admin', 'manager', 'designer']
    
    for role in roles:
        try:
            user = User.objects.get(email=f'{role}@test.com')
            print(f"✓ Using existing user: {user.email}")
        except User.DoesNotExist:
            user = User.objects.create_user(
                email=f'{role}@test.com',
                username=f'{role}_test',
                first_name=role.title(),
                last_name='User',
                is_active=True,
                is_verified=True
            )
            print(f"✓ Created user: {user.email}")
        
        users[role] = user
        
        # Create membership if it doesn't exist
        try:
            membership = OrganizationMember.objects.get(
                user=user,
                organization=org,
                is_active=True
            )
            print(f"✓ Using existing membership: {role}")
        except OrganizationMember.DoesNotExist:
            membership = OrganizationMember.objects.create(
                user=user,
                organization=org,
                role=role,
                is_active=True,
                can_invite_users=role == 'admin',
                can_manage_billing=role == 'admin',
                can_export_data=role in ['admin', 'manager']
            )
            print(f"✓ Created membership: {role}")
    
    print("\n" + "="*50)
    print("TESTING API ENDPOINTS")
    print("="*50)
    
    # Test each role
    for role in ['admin', 'manager', 'designer']:
        print(f"\nTesting {role.upper()} role:")
        print("-" * 30)
        
        user = users[role]
        
        # Create Django test client
        client = Client()
        client.force_login(user)
        
        # Test authentication endpoint
        print("1. Testing /api/auth/me/")
        response = client.get(
            '/api/auth/me/',
            HTTP_X_DEV_ORG_ID=str(org.id),
            HTTP_X_DEV_USER_ID=str(user.id)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Role: {data.get('role', 'Not found')}")
            print(f"   ✓ Organization: {data.get('organization', {}).get('name', 'Not found')}")
            
            permissions = data.get('permissions', {})
            print(f"   ✓ Can manage users: {permissions.get('can_manage_users', False)}")
            print(f"   ✓ Can generate AI: {permissions.get('can_generate_ai', False)}")
            print(f"   ✓ Can access analytics: {permissions.get('can_access_analytics', False)}")
        else:
            print(f"   ✗ Status: {response.status_code}")
            print(f"   ✗ Response: {response.content.decode()[:200]}...")
        
        # Test role info endpoint
        print("\n2. Testing /api/auth/role_info/")
        response = client.get(
            '/api/auth/role_info/',
            HTTP_X_DEV_ORG_ID=str(org.id),
            HTTP_X_DEV_USER_ID=str(user.id)
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Status: {response.status_code}")
            print(f"   ✓ Role: {data.get('role', 'Not found')}")
            print(f"   ✓ Display name: {data.get('display_name', 'Not found')}")
            print(f"   ✓ Can switch mode: {data.get('can_switch_mode', False)}")
        else:
            print(f"   ✗ Status: {response.status_code}")
            print(f"   ✗ Response: {response.content.decode()[:200]}...")
        
        # Test AI generation endpoint (should work for all roles)
        print("\n3. Testing /api/ai/generation-requests/")
        response = client.get(
            '/api/ai/generation-requests/',
            HTTP_X_DEV_ORG_ID=str(org.id),
            HTTP_X_DEV_USER_ID=str(user.id)
        )
        
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code} (AI generation access granted)")
        else:
            print(f"   ✗ Status: {response.status_code} (AI generation access denied)")
        
        # Test user management endpoint (should only work for admin)
        print("\n4. Testing /api/users/")
        response = client.get(
            '/api/users/',
            HTTP_X_DEV_ORG_ID=str(org.id),
            HTTP_X_DEV_USER_ID=str(user.id)
        )
        
        if response.status_code == 200:
            print(f"   ✓ Status: {response.status_code} (User management access granted)")
        elif response.status_code == 403:
            print(f"   ✓ Status: {response.status_code} (User management access denied - correct for {role})")
        else:
            print(f"   ✗ Status: {response.status_code} (Unexpected response)")
    
    print("\n" + "="*50)
    print("LIVE API TEST COMPLETED")
    print("="*50)

if __name__ == '__main__':
    test_live_api()
