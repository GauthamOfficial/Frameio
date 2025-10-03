"""
Playwright tests for backend APIs to identify and fix errors.
"""
import asyncio
import json
from playwright.async_api import async_playwright
import os
import sys
import django

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization, OrganizationMember, OrganizationInvitation
from django.test import TestCase
from django.test.client import Client
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class BackendAPITester:
    """Playwright-based backend API tester."""
    
    def __init__(self):
        self.client = APIClient()
        self.base_url = "http://localhost:8000"
        self.test_data = {}
        
    async def setup_test_data(self):
        """Set up test data for API testing."""
        print("🔧 Setting up test data...")
        
        # Create test organization
        self.test_data['organization'] = Organization.objects.create(
            name='Test Organization',
            slug='test-org',
            description='Test organization for API testing',
            subscription_plan='premium',
            subscription_status='active'
        )
        
        # Create test users
        self.test_data['admin_user'] = User.objects.create(
            username='admin@test.com',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )
        
        self.test_data['manager_user'] = User.objects.create(
            username='manager@test.com',
            email='manager@test.com',
            first_name='Manager',
            last_name='User'
        )
        
        self.test_data['designer_user'] = User.objects.create(
            username='designer@test.com',
            email='designer@test.com',
            first_name='Designer',
            last_name='User'
        )
        
        # Create organization memberships
        self.test_data['admin_membership'] = OrganizationMember.objects.create(
            organization=self.test_data['organization'],
            user=self.test_data['admin_user'],
            role='admin',
            can_invite_users=True,
            can_manage_billing=True,
            can_export_data=True
        )
        
        self.test_data['manager_membership'] = OrganizationMember.objects.create(
            organization=self.test_data['organization'],
            user=self.test_data['manager_user'],
            role='manager',
            can_invite_users=True,
            can_manage_billing=False,
            can_export_data=True
        )
        
        self.test_data['designer_membership'] = OrganizationMember.objects.create(
            organization=self.test_data['organization'],
            user=self.test_data['designer_user'],
            role='designer',
            can_invite_users=False,
            can_manage_billing=False,
            can_export_data=False
        )
        
        print("✅ Test data setup complete")
    
    async def test_organization_apis(self):
        """Test organization management APIs."""
        print("\n🏢 Testing Organization APIs...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            # Test 1: List organizations (should require authentication)
            print("  📋 Testing GET /api/organizations/")
            try:
                response = await page.request.get(f"{self.base_url}/api/organizations/")
                print(f"    Status: {response.status}")
                if response.status == 403:
                    print("    ✅ Correctly requires authentication")
                else:
                    print(f"    ❌ Unexpected status: {response.status}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Test 2: Create organization
            print("  📝 Testing POST /api/organizations/")
            try:
                response = await page.request.post(
                    f"{self.base_url}/api/organizations/",
                    data=json.dumps({
                        'name': 'New Test Organization',
                        'description': 'Created via API test',
                        'website': 'https://test.com',
                        'industry': 'Technology'
                    }),
                    headers={'Content-Type': 'application/json'}
                )
                print(f"    Status: {response.status}")
                if response.status == 403:
                    print("    ✅ Correctly requires authentication")
                else:
                    print(f"    ❌ Unexpected status: {response.status}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            await browser.close()
    
    async def test_user_apis(self):
        """Test user management APIs."""
        print("\n👥 Testing User APIs...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            # Test 1: List users
            print("  📋 Testing GET /api/users/")
            try:
                response = await page.request.get(f"{self.base_url}/api/users/")
                print(f"    Status: {response.status}")
                if response.status == 403:
                    print("    ✅ Correctly requires authentication")
                else:
                    print(f"    ❌ Unexpected status: {response.status}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            # Test 2: Invite user
            print("  📧 Testing POST /api/users/invite_user/")
            try:
                response = await page.request.post(
                    f"{self.base_url}/api/users/invite_user/",
                    data=json.dumps({
                        'email': 'newuser@test.com',
                        'role': 'designer',
                        'message': 'Welcome to our organization!'
                    }),
                    headers={'Content-Type': 'application/json'}
                )
                print(f"    Status: {response.status}")
                if response.status == 403:
                    print("    ✅ Correctly requires authentication")
                else:
                    print(f"    ❌ Unexpected status: {response.status}")
            except Exception as e:
                print(f"    ❌ Error: {e}")
            
            await browser.close()
    
    async def test_authenticated_apis(self):
        """Test APIs with authentication."""
        print("\n🔐 Testing Authenticated APIs...")
        
        # Use Django test client for authenticated requests
        client = Client()
        
        # Test 1: List organizations with authentication
        print("  📋 Testing authenticated GET /api/organizations/")
        try:
            # Simulate authentication by setting user in session
            client.force_login(self.test_data['admin_user'])
            response = client.get('/api/organizations/')
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                print("    ✅ Successfully retrieved organizations")
                data = response.json()
                print(f"    📊 Found {len(data.get('results', []))} organizations")
            else:
                print(f"    ❌ Unexpected status: {response.status_code}")
                print(f"    📄 Response: {response.content.decode()}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        # Test 2: List users with authentication
        print("  👥 Testing authenticated GET /api/users/")
        try:
            response = client.get('/api/users/')
            print(f"    Status: {response.status_code}")
            if response.status_code == 200:
                print("    ✅ Successfully retrieved users")
                data = response.json()
                print(f"    📊 Found {len(data.get('results', []))} users")
            else:
                print(f"    ❌ Unexpected status: {response.status_code}")
                print(f"    📄 Response: {response.content.decode()}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
    
    async def test_api_endpoints(self):
        """Test all API endpoints systematically."""
        print("\n🌐 Testing All API Endpoints...")
        
        endpoints = [
            ('GET', '/api/organizations/', 'List organizations'),
            ('POST', '/api/organizations/', 'Create organization'),
            ('GET', '/api/users/', 'List users'),
            ('POST', '/api/users/invite_user/', 'Invite user'),
            ('GET', '/api/users/permissions/', 'Get permissions'),
        ]
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            
            for method, endpoint, description in endpoints:
                print(f"  🔍 Testing {method} {endpoint} - {description}")
                try:
                    if method == 'GET':
                        response = await page.request.get(f"{self.base_url}{endpoint}")
                    elif method == 'POST':
                        response = await page.request.post(
                            f"{self.base_url}{endpoint}",
                            data=json.dumps({}),
                            headers={'Content-Type': 'application/json'}
                        )
                    
                    print(f"    Status: {response.status}")
                    
                    if response.status == 403:
                        print("    ✅ Correctly requires authentication")
                    elif response.status == 404:
                        print("    ❌ Endpoint not found")
                    elif response.status == 405:
                        print("    ❌ Method not allowed")
                    else:
                        print(f"    ⚠️  Unexpected status: {response.status}")
                        
                except Exception as e:
                    print(f"    ❌ Error: {e}")
            
            await browser.close()
    
    async def run_all_tests(self):
        """Run all API tests."""
        print("🚀 Starting Backend API Testing with Playwright")
        print("=" * 60)
        
        # Setup test data
        await self.setup_test_data()
        
        # Run tests
        await self.test_api_endpoints()
        await self.test_organization_apis()
        await self.test_user_apis()
        await self.test_authenticated_apis()
        
        print("\n" + "=" * 60)
        print("✅ Backend API testing completed!")
    
    def cleanup_test_data(self):
        """Clean up test data."""
        print("\n🧹 Cleaning up test data...")
        try:
            # Delete test data in reverse order
            OrganizationInvitation.objects.filter(
                organization=self.test_data['organization']
            ).delete()
            
            OrganizationMember.objects.filter(
                organization=self.test_data['organization']
            ).delete()
            
            User.objects.filter(
                email__in=['admin@test.com', 'manager@test.com', 'designer@test.com']
            ).delete()
            
            self.test_data['organization'].delete()
            
            print("✅ Test data cleaned up")
        except Exception as e:
            print(f"❌ Error cleaning up: {e}")


async def main():
    """Main test runner."""
    tester = BackendAPITester()
    
    try:
        await tester.run_all_tests()
    finally:
        tester.cleanup_test_data()


if __name__ == "__main__":
    asyncio.run(main())
