#!/usr/bin/env python
"""
Comprehensive verification script to test all Phase 1, Week 1 deliverables.
"""
import os
import sys
import django
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from organizations.models import Organization, OrganizationMember, OrganizationInvitation
from users.models import User, UserSession, UserActivity

User = get_user_model()

class DeliverableVerification:
    """Comprehensive verification of all deliverables."""
    
    def __init__(self):
        self.results = {}
        self.client = APIClient()
        self.test_user = None
        self.test_org = None
        self.test_membership = None
    
    def setup_test_data(self):
        """Set up test data for verification."""
        try:
            # Create test user
            self.test_user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            
            # Create test organization
            self.test_org = Organization.objects.create(
                name='Test Organization',
                slug='test-org',
                description='Test organization for verification'
            )
            
            # Create test membership
            self.test_membership = OrganizationMember.objects.create(
                organization=self.test_org,
                user=self.test_user,
                role='owner',
                can_invite_users=True,
                can_manage_billing=True,
                can_export_data=True
            )
            
            return True
        except Exception as e:
            print(f"❌ Failed to setup test data: {e}")
            return False
    
    def cleanup_test_data(self):
        """Clean up test data."""
        try:
            if self.test_membership:
                self.test_membership.delete()
            if self.test_org:
                self.test_org.delete()
            if self.test_user:
                self.test_user.delete()
            return True
        except Exception as e:
            print(f"⚠️  Warning: Failed to cleanup test data: {e}")
            return False
    
    def verify_django_setup(self):
        """Verify Django project setup."""
        print("\n🔍 Verifying Django Project Setup...")
        
        try:
            # Check Django settings
            from django.conf import settings
            
            checks = {
                'INSTALLED_APPS': 'organizations' in settings.INSTALLED_APPS,
                'AUTH_USER_MODEL': settings.AUTH_USER_MODEL == 'users.User',
                'REST_FRAMEWORK': hasattr(settings, 'REST_FRAMEWORK'),
                'CORS_HEADERS': 'corsheaders' in settings.INSTALLED_APPS,
                'DATABASE': settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3',
            }
            
            for check, result in checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['django_setup'] = all(checks.values())
            return all(checks.values())
            
        except Exception as e:
            print(f"  ❌ Django setup verification failed: {e}")
            self.results['django_setup'] = False
            return False
    
    def verify_database_models(self):
        """Verify database models are working."""
        print("\n🔍 Verifying Database Models...")
        
        try:
            # Test Organization model
            org = Organization.objects.create(
                name='Verification Org',
                slug='verification-org',
                description='Test organization'
            )
            
            # Test model methods
            org_methods = {
                'is_active': org.is_active,
                'can_generate_ai': org.can_generate_ai,
                'increment_ai_usage': True
            }
            
            # Test increment_ai_usage
            initial_usage = org.ai_generations_used
            org.increment_ai_usage()
            org.refresh_from_db()
            org_methods['increment_ai_usage'] = org.ai_generations_used == initial_usage + 1
            
            # Test User model
            user = User.objects.create_user(
                username='verification_user',
                email='verification@example.com',
                password='testpass123'
            )
            
            user_methods = {
                'full_name': user.full_name == 'verification_user',
                'get_organizations': len(user.get_organizations()) == 0,
                'can_access_organization': not user.can_access_organization(org)
            }
            
            # Test OrganizationMember model
            membership = OrganizationMember.objects.create(
                organization=org,
                user=user,
                role='admin'
            )
            
            membership_methods = {
                'is_owner': not membership.is_owner,
                'is_admin': membership.is_admin,
                'can_manage_users': membership.can_manage_users
            }
            
            # Test OrganizationInvitation model
            invitation = OrganizationInvitation.objects.create(
                organization=org,
                email='invitee@example.com',
                role='designer',
                invited_by=user,
                token='test-token'
            )
            
            invitation_methods = {
                'is_expired': not invitation.is_expired,
                'accept': invitation.accept(user),
                'decline': invitation.decline()
            }
            
            # Clean up test data
            invitation.delete()
            membership.delete()
            user.delete()
            org.delete()
            
            # Check results
            all_checks = {
                'Organization methods': all(org_methods.values()),
                'User methods': all(user_methods.values()),
                'Membership methods': all(membership_methods.values()),
                'Invitation methods': all(invitation_methods.values())
            }
            
            for check, result in all_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['database_models'] = all(all_checks.values())
            return all(all_checks.values())
            
        except Exception as e:
            print(f"  ❌ Database models verification failed: {e}")
            self.results['database_models'] = False
            return False
    
    def verify_authentication(self):
        """Verify authentication system."""
        print("\n🔍 Verifying Authentication System...")
        
        try:
            # Test user creation and authentication
            user = User.objects.create_user(
                username='auth_test',
                email='auth@example.com',
                password='testpass123'
            )
            
            # Test authentication
            from django.contrib.auth import authenticate
            auth_user = authenticate(username='auth_test', password='testpass123')
            
            auth_checks = {
                'User creation': user is not None,
                'Authentication': auth_user is not None,
                'Password check': user.check_password('testpass123'),
                'User properties': user.is_active and not user.is_staff
            }
            
            # Test Clerk authentication class
            from users.authentication import ClerkAuthentication
            clerk_auth = ClerkAuthentication()
            
            auth_checks['Clerk auth class'] = clerk_auth is not None
            
            # Clean up
            user.delete()
            
            for check, result in auth_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['authentication'] = all(auth_checks.values())
            return all(auth_checks.values())
            
        except Exception as e:
            print(f"  ❌ Authentication verification failed: {e}")
            self.results['authentication'] = False
            return False
    
    def verify_api_endpoints(self):
        """Verify API endpoints are working."""
        print("\n🔍 Verifying API Endpoints...")
        
        try:
            # Test without authentication
            response = self.client.get('/api/organizations/')
            unauthenticated_ok = response.status_code in [401, 403]
            
            # Test with authentication
            self.client.force_authenticate(user=self.test_user)
            
            # Test organization list
            response = self.client.get('/api/organizations/')
            org_list_ok = response.status_code == 200
            
            # Test organization creation
            org_data = {
                'name': 'API Test Organization',
                'description': 'Test organization via API',
                'website': 'https://test.com',
                'industry': 'Technology'
            }
            response = self.client.post('/api/organizations/', org_data)
            org_creation_ok = response.status_code == 201
            
            # Test organization details
            if org_creation_ok:
                org_id = response.data['id']
                response = self.client.get(f'/api/organizations/{org_id}/')
                org_details_ok = response.status_code == 200
                
                # Test organization members
                response = self.client.get(f'/api/organizations/{org_id}/members/')
                members_ok = response.status_code == 200
                
                # Test organization usage
                response = self.client.get(f'/api/organizations/{org_id}/usage/')
                usage_ok = response.status_code == 200
                
                # Test invitation
                invite_data = {
                    'email': 'newuser@example.com',
                    'role': 'designer'
                }
                response = self.client.post(f'/api/organizations/{org_id}/invite_member/', invite_data)
                invitation_ok = response.status_code == 201
                
                # Clean up created organization
                Organization.objects.filter(id=org_id).delete()
            else:
                org_details_ok = members_ok = usage_ok = invitation_ok = False
            
            api_checks = {
                'Unauthenticated access': unauthenticated_ok,
                'Organization list': org_list_ok,
                'Organization creation': org_creation_ok,
                'Organization details': org_details_ok,
                'Organization members': members_ok,
                'Organization usage': usage_ok,
                'Organization invitation': invitation_ok
            }
            
            for check, result in api_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['api_endpoints'] = all(api_checks.values())
            return all(api_checks.values())
            
        except Exception as e:
            print(f"  ❌ API endpoints verification failed: {e}")
            self.results['api_endpoints'] = False
            return False
    
    def verify_multi_tenancy(self):
        """Verify multi-tenancy is working."""
        print("\n🔍 Verifying Multi-Tenancy...")
        
        try:
            # Create two organizations
            org1 = Organization.objects.create(
                name='Organization 1',
                slug='org-1',
                description='First organization'
            )
            org2 = Organization.objects.create(
                name='Organization 2',
                slug='org-2',
                description='Second organization'
            )
            
            # Create users for each organization
            user1 = User.objects.create_user(
                username='user1',
                email='user1@example.com',
                password='testpass123'
            )
            user2 = User.objects.create_user(
                username='user2',
                email='user2@example.com',
                password='testpass123'
            )
            
            # Create memberships
            membership1 = OrganizationMember.objects.create(
                organization=org1,
                user=user1,
                role='owner'
            )
            membership2 = OrganizationMember.objects.create(
                organization=org2,
                user=user2,
                role='owner'
            )
            
            # Test tenant isolation
            tenant_checks = {
                'User1 org access': user1.can_access_organization(org1),
                'User1 org isolation': not user1.can_access_organization(org2),
                'User2 org access': user2.can_access_organization(org2),
                'User2 org isolation': not user2.can_access_organization(org1),
                'User1 organizations': org1 in user1.get_organizations(),
                'User1 org isolation list': org2 not in user1.get_organizations(),
                'User2 organizations': org2 in user2.get_organizations(),
                'User2 org isolation list': org1 not in user2.get_organizations()
            }
            
            # Clean up
            membership1.delete()
            membership2.delete()
            user1.delete()
            user2.delete()
            org1.delete()
            org2.delete()
            
            for check, result in tenant_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['multi_tenancy'] = all(tenant_checks.values())
            return all(tenant_checks.values())
            
        except Exception as e:
            print(f"  ❌ Multi-tenancy verification failed: {e}")
            self.results['multi_tenancy'] = False
            return False
    
    def verify_usage_tracking(self):
        """Verify usage tracking is working."""
        print("\n🔍 Verifying Usage Tracking...")
        
        try:
            # Create organization
            org = Organization.objects.create(
                name='Usage Test Org',
                slug='usage-test',
                description='Organization for usage testing'
            )
            
            # Test initial usage
            initial_usage = org.ai_generations_used
            initial_limit = org.ai_generations_limit
            can_generate = org.can_generate_ai
            
            # Test usage increment
            org.increment_ai_usage()
            org.refresh_from_db()
            
            # Test usage limit
            org.ai_generations_used = org.ai_generations_limit
            org.save()
            
            usage_checks = {
                'Initial usage': initial_usage == 0,
                'Initial limit': initial_limit == 10,
                'Initial can generate': can_generate,
                'Usage increment': org.ai_generations_used == 1,
                'Usage limit reached': not org.can_generate_ai,
                'Usage percentage': org.ai_generations_used / org.ai_generations_limit == 1.0
            }
            
            # Clean up
            org.delete()
            
            for check, result in usage_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['usage_tracking'] = all(usage_checks.values())
            return all(usage_checks.values())
            
        except Exception as e:
            print(f"  ❌ Usage tracking verification failed: {e}")
            self.results['usage_tracking'] = False
            return False
    
    def verify_environment_config(self):
        """Verify environment configuration."""
        print("\n🔍 Verifying Environment Configuration...")
        
        try:
            from django.conf import settings
            
            env_checks = {
                'SECRET_KEY': hasattr(settings, 'SECRET_KEY') and settings.SECRET_KEY,
                'DEBUG': hasattr(settings, 'DEBUG'),
                'ALLOWED_HOSTS': hasattr(settings, 'ALLOWED_HOSTS'),
                'DATABASES': hasattr(settings, 'DATABASES'),
                'REST_FRAMEWORK': hasattr(settings, 'REST_FRAMEWORK'),
                'CORS_ALLOWED_ORIGINS': hasattr(settings, 'CORS_ALLOWED_ORIGINS'),
                'CLERK_PUBLISHABLE_KEY': hasattr(settings, 'CLERK_PUBLISHABLE_KEY'),
                'CLERK_SECRET_KEY': hasattr(settings, 'CLERK_SECRET_KEY'),
                'ARCJET_KEY': hasattr(settings, 'ARCJET_KEY'),
                'NANOBANANA_API_KEY': hasattr(settings, 'NANOBANANA_API_KEY'),
                'LOGGING': hasattr(settings, 'LOGGING'),
                'MEDIA_URL': hasattr(settings, 'MEDIA_URL'),
                'MEDIA_ROOT': hasattr(settings, 'MEDIA_ROOT')
            }
            
            for check, result in env_checks.items():
                if result:
                    print(f"  ✅ {check}: OK")
                else:
                    print(f"  ❌ {check}: FAILED")
            
            self.results['environment_config'] = all(env_checks.values())
            return all(env_checks.values())
            
        except Exception as e:
            print(f"  ❌ Environment configuration verification failed: {e}")
            self.results['environment_config'] = False
            return False
    
    def run_all_verifications(self):
        """Run all verification tests."""
        print("🚀 Frameio Multi-Tenant Django Backend - Deliverable Verification")
        print("=" * 80)
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Failed to setup test data. Aborting verification.")
            return False
        
        try:
            # Run all verifications
            verifications = [
                self.verify_django_setup,
                self.verify_database_models,
                self.verify_authentication,
                self.verify_api_endpoints,
                self.verify_multi_tenancy,
                self.verify_usage_tracking,
                self.verify_environment_config
            ]
            
            for verification in verifications:
                verification()
            
            # Print summary
            print("\n" + "=" * 80)
            print("📊 VERIFICATION SUMMARY")
            print("=" * 80)
            
            total_checks = len(self.results)
            passed_checks = sum(1 for result in self.results.values() if result)
            
            for check, result in self.results.items():
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"{check.replace('_', ' ').title()}: {status}")
            
            print(f"\nOverall Result: {passed_checks}/{total_checks} checks passed")
            
            if passed_checks == total_checks:
                print("\n🎉 ALL DELIVERABLES ARE WORKING CORRECTLY!")
                print("✅ Phase 1, Week 1, Team Member 1 tasks completed successfully!")
                return True
            else:
                print(f"\n⚠️  {total_checks - passed_checks} deliverables need attention.")
                return False
                
        finally:
            # Cleanup
            self.cleanup_test_data()

def main():
    """Main verification function."""
    verifier = DeliverableVerification()
    success = verifier.run_all_verifications()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
