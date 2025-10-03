#!/usr/bin/env python
"""
Test RBAC by starting the Django server and making actual HTTP requests.
"""

import os
import sys
import django
import requests
import json
import time
import subprocess
import threading
from urllib.parse import urljoin

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember

User = get_user_model()

def start_django_server():
    """Start Django development server in background."""
    print("Starting Django development server...")
    
    # Start server in background
    process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '8000'
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Wait for server to start
    time.sleep(5)
    
    return process

def test_rbac_with_server():
    """Test RBAC with actual HTTP requests to running server."""
    print("RBAC SERVER TEST")
    print("="*50)
    
    # Start server
    server_process = start_django_server()
    
    try:
        base_url = "http://localhost:8000"
        
        # Test server is running
        try:
            response = requests.get(f"{base_url}/api/", timeout=5)
            print("✓ Django server is running")
        except requests.exceptions.RequestException:
            print("❌ Django server not responding")
            return
        
        # Create test data
        print("\nSetting up test data...")
        
        # Create organization
        org, created = Organization.objects.get_or_create(
            slug='test-rbac-org',
            defaults={
                'name': 'Test RBAC Organization',
                'description': 'Organization for testing RBAC',
                'subscription_plan': 'premium',
                'subscription_status': 'active'
            }
        )
        print(f"✓ Organization: {org.name}")
        
        # Create test users
        users = {}
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
            users[role] = user
            
            # Create membership
            membership, created = OrganizationMember.objects.get_or_create(
                user=user,
                organization=org,
                defaults={
                    'role': role,
                    'is_active': True,
                    'can_invite_users': role == 'admin',
                    'can_manage_billing': role == 'admin',
                    'can_export_data': role in ['admin', 'manager']
                }
            )
            print(f"✓ User: {user.email} ({role})")
        
        print("\n" + "="*50)
        print("TESTING API ENDPOINTS")
        print("="*50)
        
        # Test each role
        for role in ['admin', 'manager', 'designer']:
            print(f"\nTesting {role.upper()} role:")
            print("-" * 30)
            
            user = users[role]
            
            # Test authentication endpoint
            print("1. Testing /api/auth/me/")
            try:
                response = requests.get(
                    f"{base_url}/api/auth/me/",
                    headers={
                        'X-Dev-Org-ID': str(org.id),
                        'X-Dev-User-ID': str(user.id)
                    },
                    timeout=10
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
                    print(f"   ✗ Response: {response.text[:200]}...")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Request failed: {e}")
            
            # Test role info endpoint
            print("\n2. Testing /api/auth/role_info/")
            try:
                response = requests.get(
                    f"{base_url}/api/auth/role_info/",
                    headers={
                        'X-Dev-Org-ID': str(org.id),
                        'X-Dev-User-ID': str(user.id)
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✓ Status: {response.status_code}")
                    print(f"   ✓ Role: {data.get('role', 'Not found')}")
                    print(f"   ✓ Display name: {data.get('display_name', 'Not found')}")
                    print(f"   ✓ Can switch mode: {data.get('can_switch_mode', False)}")
                else:
                    print(f"   ✗ Status: {response.status_code}")
                    print(f"   ✗ Response: {response.text[:200]}...")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Request failed: {e}")
            
            # Test AI generation endpoint
            print("\n3. Testing /api/ai/generation-requests/")
            try:
                response = requests.get(
                    f"{base_url}/api/ai/generation-requests/",
                    headers={
                        'X-Dev-Org-ID': str(org.id),
                        'X-Dev-User-ID': str(user.id)
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✓ Status: {response.status_code} (AI generation access granted)")
                else:
                    print(f"   ✗ Status: {response.status_code} (AI generation access denied)")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Request failed: {e}")
            
            # Test user management endpoint
            print("\n4. Testing /api/users/")
            try:
                response = requests.get(
                    f"{base_url}/api/users/",
                    headers={
                        'X-Dev-Org-ID': str(org.id),
                        'X-Dev-User-ID': str(user.id)
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"   ✓ Status: {response.status_code} (User management access granted)")
                elif response.status_code == 403:
                    print(f"   ✓ Status: {response.status_code} (User management access denied - correct for {role})")
                else:
                    print(f"   ✗ Status: {response.status_code} (Unexpected response)")
            except requests.exceptions.RequestException as e:
                print(f"   ✗ Request failed: {e}")
        
        print("\n" + "="*50)
        print("RBAC SERVER TEST COMPLETED")
        print("="*50)
        
    finally:
        # Stop server
        print("\nStopping Django server...")
        server_process.terminate()
        server_process.wait()
        print("✓ Server stopped")

if __name__ == '__main__':
    test_rbac_with_server()
