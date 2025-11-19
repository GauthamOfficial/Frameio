"""
Quick test script to check if branding kits are being saved and retrieved correctly
Run this from the backend directory: python test_branding_kit.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.models import GeneratedBrandingKit
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("Branding Kit Database Test")
print("=" * 60)

# Check if table exists
try:
    total_kits = GeneratedBrandingKit.objects.count()
    print(f"\n[OK] Database table exists")
    print(f"  Total branding kits in database: {total_kits}")
    
    if total_kits > 0:
        print("\nRecent branding kits:")
        recent_kits = GeneratedBrandingKit.objects.all()[:5]
        for kit in recent_kits:
            print(f"  - ID: {kit.id}")
            print(f"    Prompt: {kit.prompt[:50]}...")
            print(f"    User: {kit.user.email if kit.user else 'None'}")
            print(f"    Organization: {kit.organization.name if kit.organization else 'None'}")
            print(f"    Created: {kit.created_at}")
            print(f"    Has logo: {bool(kit.logo_data)}")
            print(f"    Has palette: {bool(kit.color_palette_data)}")
            print()
    else:
        print("\n[WARNING] No branding kits found in database")
        print("  This could mean:")
        print("  1. No branding kits have been generated yet")
        print("  2. The branding kits were generated without authentication")
        print("  3. There's an issue with saving to the database")
        
        # Check if there are any users
        user_count = User.objects.count()
        print(f"\n  Users in database: {user_count}")
        if user_count > 0:
            users = User.objects.all()[:3]
            print("  Sample users:")
            for user in users:
                print(f"    - {user.email if hasattr(user, 'email') else user.username}")
    
except Exception as e:
    print(f"\nX Error accessing database: {e}")
    print("  This might mean:")
    print("  1. The migration hasn't been run: python manage.py migrate")
    print("  2. There's a database connection issue")
    print(f"  3. Error details: {str(e)}")

print("\n" + "=" * 60)
