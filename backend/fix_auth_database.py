#!/usr/bin/env python
"""
Fix authentication issues by ensuring database is set up correctly
Run with: python fix_auth_database.py
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import connection
from organizations.models import Organization, OrganizationMember
import uuid

User = get_user_model()

def check_database_connection():
    """Check if database is connected"""
    print("\n🔍 Checking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def check_migrations():
    """Check if all migrations are applied"""
    print("\n🔍 Checking migrations...")
    from django.core.management import call_command
    from io import StringIO
    
    try:
        out = StringIO()
        call_command('showmigrations', '--plan', stdout=out)
        output = out.getvalue()
        
        # Check if there are unapplied migrations
        if '[ ]' in output:
            print("⚠️  Some migrations are not applied")
            print("   Run: python manage.py migrate")
            return False
        else:
            print("✅ All migrations are applied")
            return True
    except Exception as e:
        print(f"⚠️  Could not check migrations: {e}")
        return False

def create_test_user():
    """Create or get test user"""
    print("\n🔍 Creating/getting test user...")
    
    try:
        # Try to get existing user
        user = User.objects.filter(email='test@example.com').first()
        
        if user:
            print(f"✅ Test user already exists: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            print(f"   Is active: {user.is_active}")
            return user
        else:
            # Create new user
            print("   Creating new test user...")
            user = User.objects.create_user(
                email='test@example.com',
                username='testuser',
                password='testpass123',
                first_name='Test',
                last_name='User'
            )
            user.is_active = True
            user.save()
            
            print(f"✅ Test user created: {user.email}")
            print(f"   User ID: {user.id}")
            print(f"   Username: {user.username}")
            return user
            
    except Exception as e:
        print(f"❌ Failed to create test user: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_test_organization(user):
    """Create or get test organization"""
    print("\n🔍 Creating/getting test organization...")
    
    try:
        # Try to get existing organization
        org = Organization.objects.filter(name='Test Organization').first()
        
        if org:
            print(f"✅ Test organization already exists: {org.name}")
            print(f"   Org ID: {org.id}")
        else:
            # Create new organization
            print("   Creating new test organization...")
            org = Organization.objects.create(
                name='Test Organization',
                slug='test-org',
                owner=user
            )
            print(f"✅ Test organization created: {org.name}")
            print(f"   Org ID: {org.id}")
        
        # Check/create membership
        membership, created = OrganizationMember.objects.get_or_create(
            user=user,
            organization=org,
            defaults={
                'role': 'admin',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created membership for {user.email} in {org.name}")
        else:
            print(f"✅ Membership already exists for {user.email} in {org.name}")
        
        return org
        
    except Exception as e:
        print(f"❌ Failed to create test organization: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_authentication():
    """Test authentication with test user"""
    print("\n🔍 Testing authentication...")
    
    try:
        user = User.objects.filter(email='test@example.com').first()
        if not user:
            print("❌ Test user not found")
            return False
        
        # Test authentication
        from users.authentication import DevelopmentAuthentication
        
        print(f"✅ Test user found: {user.email}")
        print(f"   User is active: {user.is_active}")
        print(f"   User is staff: {user.is_staff}")
        print(f"   User is superuser: {user.is_superuser}")
        
        return True
        
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def check_auth_settings():
    """Check authentication settings"""
    print("\n🔍 Checking authentication settings...")
    
    from django.conf import settings
    
    try:
        auth_classes = settings.REST_FRAMEWORK.get('DEFAULT_AUTHENTICATION_CLASSES', [])
        print("✅ Authentication classes configured:")
        for auth_class in auth_classes:
            print(f"   - {auth_class}")
        
        print(f"\n   DEBUG mode: {settings.DEBUG}")
        print(f"   CLERK_CONFIGURED: {getattr(settings, 'CLERK_CONFIGURED', False)}")
        
        return True
    except Exception as e:
        print(f"❌ Could not check auth settings: {e}")
        return False

def main():
    print("🚀 Starting Database and Authentication Fix")
    print("=" * 60)
    
    # Step 1: Check database connection
    if not check_database_connection():
        print("\n❌ FATAL: Database connection failed")
        print("   Please check your database configuration in .env")
        sys.exit(1)
    
    # Step 2: Check migrations
    migrations_ok = check_migrations()
    if not migrations_ok:
        print("\n⚠️  Please run migrations first:")
        print("   python manage.py migrate")
        response = input("\nDo you want to run migrations now? (y/n): ")
        if response.lower() == 'y':
            from django.core.management import call_command
            print("\n   Running migrations...")
            call_command('migrate')
            print("✅ Migrations completed")
        else:
            print("   Skipping migrations")
    
    # Step 3: Create test user
    user = create_test_user()
    if not user:
        print("\n❌ FATAL: Could not create test user")
        sys.exit(1)
    
    # Step 4: Create test organization
    org = create_test_organization(user)
    if not org:
        print("\n⚠️  Could not create test organization")
    
    # Step 5: Test authentication
    test_authentication()
    
    # Step 6: Check auth settings
    check_auth_settings()
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print("✅ Database is connected")
    print(f"✅ Test user exists: test@example.com")
    print(f"✅ User ID: {user.id}")
    if org:
        print(f"✅ Test organization exists: {org.name}")
        print(f"✅ Organization ID: {org.id}")
    print("\n🎉 Setup complete!")
    print("\nYou can now test the API with:")
    print(f"   Authorization: Bearer test_clerk_token")
    print("\nOr use development headers:")
    print(f"   X-Dev-User-ID: {user.id}")
    if org:
        print(f"   X-Dev-Org-ID: {org.id}")
    print("=" * 60)

if __name__ == '__main__':
    main()






