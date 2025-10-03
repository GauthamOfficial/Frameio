"""
Debug API errors by testing endpoints directly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from organizations.models import Organization, OrganizationMember

User = get_user_model()


def test_api_endpoints():
    """Test API endpoints to identify errors."""
    print("🚀 Testing Backend API Endpoints")
    print("=" * 50)
    
    # Create test data
    print("🔧 Setting up test data...")
    
    # Create organization
    org = Organization.objects.create(
        name='Test Organization',
        slug='test-org',
        description='Test organization',
        subscription_plan='premium',
        subscription_status='active'
    )
    print(f"✅ Created organization: {org.name}")
    
    # Create admin user
    admin_user = User.objects.create(
        username='admin@test.com',
        email='admin@test.com',
        first_name='Admin',
        last_name='User'
    )
    print(f"✅ Created admin user: {admin_user.email}")
    
    # Create membership
    membership = OrganizationMember.objects.create(
        organization=org,
        user=admin_user,
        role='admin',
        can_invite_users=True,
        can_manage_billing=True,
        can_export_data=True
    )
    print(f"✅ Created membership: {membership.role}")
    
    # Test API endpoints
    client = APIClient()
    
    print("\n📋 Testing API Endpoints:")
    print("-" * 30)
    
    # Test 1: List organizations without auth
    print("1. GET /api/organizations/ (no auth)")
    response = client.get('/api/organizations/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 403:
        print("   ✅ Correctly requires authentication")
    else:
        print(f"   ❌ Unexpected: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 2: List organizations with auth
    print("\n2. GET /api/organizations/ (with auth)")
    client.force_authenticate(user=admin_user)
    response = client.get('/api/organizations/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: Found {len(data.get('results', []))} organizations")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 3: Get organization details
    print(f"\n3. GET /api/organizations/{org.id}/")
    response = client.get(f'/api/organizations/{org.id}/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Success: Retrieved organization details")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 4: List users
    print("\n4. GET /api/users/")
    response = client.get('/api/users/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: Found {len(data.get('results', []))} users")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 5: Invite user
    print("\n5. POST /api/users/invite_user/")
    data = {
        'email': 'newuser@test.com',
        'role': 'designer',
        'message': 'Welcome!'
    }
    response = client.post('/api/users/invite_user/', data, format='json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   ✅ Success: User invited")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 6: Get user permissions
    print("\n6. GET /api/users/permissions/")
    response = client.get('/api/users/permissions/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: Role = {data.get('role')}")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 7: Organization members
    print(f"\n7. GET /api/organizations/{org.id}/members/")
    response = client.get(f'/api/organizations/{org.id}/members/')
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Success: Found {len(data)} members")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    # Test 8: Invite member
    print(f"\n8. POST /api/organizations/{org.id}/invite_member/")
    data = {
        'email': 'newmember@test.com',
        'role': 'designer'
    }
    response = client.post(f'/api/organizations/{org.id}/invite_member/', data, format='json')
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print("   ✅ Success: Member invited")
    else:
        print(f"   ❌ Error: {response.status_code}")
        print(f"   Response: {response.content.decode()[:200]}")
    
    print("\n" + "=" * 50)
    print("✅ API testing completed!")
    
    # Cleanup
    print("\n🧹 Cleaning up...")
    membership.delete()
    admin_user.delete()
    org.delete()
    print("✅ Cleanup completed!")


if __name__ == "__main__":
    test_api_endpoints()
