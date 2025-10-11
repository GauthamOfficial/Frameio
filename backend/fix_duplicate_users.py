#!/usr/bin/env python3
"""
Fix duplicate users in the database
"""
import os
import sys
import django

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from organizations.models import Organization


def fix_duplicate_users():
    """Fix duplicate users in the database"""
    print("🔧 Fixing duplicate users...")
    
    try:
        User = get_user_model()
        
        # Find users with duplicate emails
        from django.db.models import Count
        duplicate_emails = User.objects.values('email').annotate(
            count=Count('email')
        ).filter(count__gt=1)
        
        print(f"📊 Found {len(duplicate_emails)} duplicate email addresses")
        
        for duplicate in duplicate_emails:
            email = duplicate['email']
            print(f"🔍 Processing duplicates for: {email}")
            
            # Get all users with this email
            users = User.objects.filter(email=email).order_by('id')
            print(f"  Found {users.count()} users with email {email}")
            
            # Keep the first one, delete the rest
            keep_user = users.first()
            delete_users = users.exclude(id=keep_user.id)
            
            print(f"  Keeping user ID: {keep_user.id}")
            print(f"  Deleting {delete_users.count()} duplicate users")
            
            for user in delete_users:
                print(f"    Deleting user ID: {user.id}")
                user.delete()
        
        print("✅ Duplicate users fixed!")
        return True
        
    except Exception as e:
        print(f"❌ Error fixing duplicate users: {str(e)}")
        return False


def create_clean_test_data():
    """Create clean test data"""
    print("\n🧹 Creating clean test data...")
    
    try:
        User = get_user_model()
        
        # Delete existing test users
        User.objects.filter(email__in=[
            'test@example.com',
            'testuser@example.com',
            'admin@example.com'
        ]).delete()
        
        # Create clean test user
        user, created = User.objects.get_or_create(
            email='test@example.com',
            defaults={
                'first_name': 'Test',
                'last_name': 'User',
                'is_active': True
            }
        )
        
        if created:
            print(f"✅ Created test user: {user.email}")
        else:
            print(f"✅ Using existing test user: {user.email}")
        
        # Create clean test organization
        org, created = Organization.objects.get_or_create(
            name='Test Organization',
            defaults={
                'description': 'Test organization for Gemini integration'
            }
        )
        
        if created:
            print(f"✅ Created test organization: {org.name}")
        else:
            print(f"✅ Using existing test organization: {org.name}")
        
        return user, org
        
    except Exception as e:
        print(f"❌ Error creating clean test data: {str(e)}")
        return None, None


def test_after_cleanup():
    """Test after cleanup"""
    print("\n🧪 Testing after cleanup...")
    
    try:
        # AI image generation has been disabled
        
        # Get clean test data
        user, org = create_clean_test_data()
        
        if not user or not org:
            print("❌ Could not create clean test data")
            return False
        
        # Test poster generator
        poster_generator = TextilePosterGenerator()
        
        result = poster_generator.generate_poster_with_caption(
            organization=org,
            user=user,
            fabric_type='silk saree',
            festival='deepavali',
            price_range='₹2999',
            style='elegant',
            custom_text='Special Diwali Collection',
            offer_details='30% Off on all items'
        )
        
        if result.get('success'):
            print("✅ Poster generator working after cleanup!")
            print(f"🖼️  Poster URL: {result.get('poster_url', 'N/A')}")
            print(f"📊 Service: {result.get('service', 'N/A')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 'N/A')}s")
            print(f"🆔 Request ID: {result.get('request_id', 'N/A')}")
            
            # Check if it's using Gemini 2.5 Flash
            service = result.get('service', '')
            if 'gemini' in service.lower():
                print("🎉 SUCCESS: Using Gemini 2.5 Flash!")
                return True
            else:
                print(f"⚠️  Using service: {service} (not Gemini)")
                return False
        else:
            print(f"❌ Poster generator failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing after cleanup: {str(e)}")
        return False


def run_cleanup_and_test():
    """Run cleanup and test"""
    print("🚀 Starting Database Cleanup and Test")
    print("=" * 50)
    
    # Step 1: Fix duplicate users
    print("\n📋 Step 1: Fixing duplicate users...")
    if not fix_duplicate_users():
        print("❌ Failed to fix duplicate users")
        return False
    
    # Step 2: Test after cleanup
    print("\n📋 Step 2: Testing after cleanup...")
    if not test_after_cleanup():
        print("❌ Test failed after cleanup")
        return False
    
    print("\n🎉 SUCCESS! Database cleaned up and Gemini 2.5 Flash is working!")
    print("🚀 Your site is NO LONGER in fallback mode!")
    return True


if __name__ == "__main__":
    success = run_cleanup_and_test()
    sys.exit(0 if success else 1)
