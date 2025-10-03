#!/usr/bin/env python
"""
Comprehensive RBAC integration test to verify the system is working correctly.
This test simulates actual HTTP requests to verify role-based access control.
"""

import os
import sys
import django
from django.conf import settings
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember
from users.roles import get_user_role_permissions
import json

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

User = get_user_model()

class RBACIntegrationTest:
    """Test RBAC system with actual HTTP requests."""
    
    def __init__(self):
        self.client = Client()
        self.org = None
        self.users = {}
        self.memberships = {}
    
    def setup_test_data(self):
        """Create test organization and users."""
        print("Setting up test data...")
        
        # Create test organization
        self.org, created = Organization.objects.get_or_create(
            slug='test-rbac-org',
            defaults={
                'name': 'Test RBAC Organization',
                'description': 'Organization for testing RBAC',
                'subscription_plan': 'premium',
                'subscription_status': 'active'
            }
        )
        print(f"✓ Organization: {self.org.name}")
        
        # Create test users
        roles = ['admin', 'manager', 'designer']
        for role in roles:
            user, created = User.objects.get_or_create(
                email=f'{role}@test.com',
                defaults={
                    'username': f'{role}_test',
                    'first_name': role.title(),
                    'last_name': 'User',
                    'is_active': True,
                    'is_verified': True
                }
            )
            self.users[role] = user
            print(f"✓ User: {user.email}")
        
        # Create organization memberships
        for role in roles:
            membership, created = OrganizationMember.objects.get_or_create(
                user=self.users[role],
                organization=self.org,
                defaults={
                    'role': role,
                    'is_active': True,
                    'can_invite_users': role == 'admin',
                    'can_manage_billing': role == 'admin',
                    'can_export_data': role in ['admin', 'manager']
                }
            )
            self.memberships[role] = membership
            print(f"✓ Membership: {role} in {self.org.name}")
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints with role context."""
        print("\n" + "="*60)
        print("TESTING AUTHENTICATION ENDPOINTS")
        print("="*60)
        
        for role in ['admin', 'manager', 'designer']:
            print(f"\nTesting {role.upper()} role:")
            print("-" * 40)
            
            # Login as user
            self.client.force_login(self.users[role])
            
            # Set organization context in headers (simulating middleware)
            response = self.client.get(
                '/api/auth/me/',
                HTTP_X_DEV_ORG_ID=str(self.org.id),
                HTTP_X_DEV_USER_ID=str(self.users[role].id)
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Authentication successful")
                print(f"  Role: {data.get('role', 'Not found')}")
                print(f"  Organization: {data.get('organization', {}).get('name', 'Not found')}")
                
                # Check permissions
                permissions = data.get('permissions', {})
                print(f"  Can manage users: {permissions.get('can_manage_users', False)}")
                print(f"  Can generate AI: {permissions.get('can_generate_ai', False)}")
                print(f"  Can access analytics: {permissions.get('can_access_analytics', False)}")
            else:
                print(f"✗ Authentication failed: {response.status_code}")
                print(f"  Response: {response.content.decode()}")
    
    def test_api_permissions(self):
        """Test API endpoint permissions."""
        print("\n" + "="*60)
        print("TESTING API PERMISSIONS")
        print("="*60)
        
        # Test endpoints with different roles
        test_endpoints = [
            ('/api/users/', 'GET', 'User management'),
            ('/api/ai/generation-requests/', 'GET', 'AI Generation'),
            ('/api/ai/analytics/dashboard/', 'GET', 'AI Analytics'),
        ]
        
        for endpoint, method, description in test_endpoints:
            print(f"\nTesting {description} ({method} {endpoint}):")
            print("-" * 50)
            
            for role in ['admin', 'manager', 'designer']:
                self.client.force_login(self.users[role])
                
                if method == 'GET':
                    response = self.client.get(
                        endpoint,
                        HTTP_X_DEV_ORG_ID=str(self.org.id),
                        HTTP_X_DEV_USER_ID=str(self.users[role].id)
                    )
                else:
                    response = self.client.post(
                        endpoint,
                        HTTP_X_DEV_ORG_ID=str(self.org.id),
                        HTTP_X_DEV_USER_ID=str(self.users[role].id)
                    )
                
                status = "✓" if response.status_code in [200, 201] else "✗"
                print(f"  {role}: {status} ({response.status_code})")
                
                if response.status_code not in [200, 201, 403, 404]:
                    print(f"    Error: {response.content.decode()[:100]}...")
    
    def test_middleware_integration(self):
        """Test middleware integration."""
        print("\n" + "="*60)
        print("TESTING MIDDLEWARE INTEGRATION")
        print("="*60)
        
        for role in ['admin', 'manager', 'designer']:
            print(f"\nTesting {role.upper()} middleware context:")
            print("-" * 40)
            
            self.client.force_login(self.users[role])
            
            # Test a simple endpoint that should work for all roles
            response = self.client.get(
                '/api/auth/role_info/',
                HTTP_X_DEV_ORG_ID=str(self.org.id),
                HTTP_X_DEV_USER_ID=str(self.users[role].id)
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Middleware working")
                print(f"  Role: {data.get('role', 'Not found')}")
                print(f"  Display name: {data.get('display_name', 'Not found')}")
                print(f"  Can switch mode: {data.get('can_switch_mode', False)}")
            else:
                print(f"✗ Middleware failed: {response.status_code}")
    
    def test_role_based_rate_limiting(self):
        """Test role-based rate limiting."""
        print("\n" + "="*60)
        print("TESTING ROLE-BASED RATE LIMITING")
        print("="*60)
        
        # Test AI generation endpoint with different roles
        for role in ['admin', 'manager', 'designer']:
            print(f"\nTesting {role.upper()} rate limits:")
            print("-" * 40)
            
            self.client.force_login(self.users[role])
            
            # Make multiple requests to test rate limiting
            success_count = 0
            rate_limited_count = 0
            
            for i in range(15):  # Try 15 requests
                response = self.client.post(
                    '/api/ai/generation-requests/',
                    json.dumps({
                        'provider': 'openai',
                        'generation_type': 'textile_poster',
                        'prompt': f'Test prompt {i}'
                    }),
                    content_type='application/json',
                    HTTP_X_DEV_ORG_ID=str(self.org.id),
                    HTTP_X_DEV_USER_ID=str(self.users[role].id)
                )
                
                if response.status_code == 201:
                    success_count += 1
                elif response.status_code == 429:
                    rate_limited_count += 1
                    break
            
            print(f"  Successful requests: {success_count}")
            print(f"  Rate limited: {rate_limited_count > 0}")
    
    def run_all_tests(self):
        """Run all RBAC tests."""
        print("RBAC INTEGRATION TEST")
        print("="*60)
        
        try:
            self.setup_test_data()
            self.test_authentication_endpoints()
            self.test_api_permissions()
            self.test_middleware_integration()
            self.test_role_based_rate_limiting()
            
            print("\n" + "="*60)
            print("RBAC INTEGRATION TEST COMPLETED")
            print("="*60)
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test = RBACIntegrationTest()
    test.run_all_tests()
