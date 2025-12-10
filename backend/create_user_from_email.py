#!/usr/bin/env python
"""
Script to create a Django user from an email address.
Useful for creating users manually or migrating existing user data.
"""
import os
import sys
import django

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def create_user_from_email(email, first_name=None, last_name=None):
    """Create or get a Django user from an email address."""
    
    print(f"\n🔍 Checking for user with email: {email}")
    
    # Check if user already exists
    user = User.objects.filter(email=email).first()
    
    if user:
        print(f"✅ User already exists in Django database!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Created At: {user.created_at}")
        return user
    
    # Extract username from email (part before @)
    username = email.split('@')[0]
    
    # Make username unique if it already exists
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    # Extract first and last name from email if not provided
    if not first_name and not last_name:
        # Try to extract from email (e.g., kumargautham28official -> Kumargautham)
        name_parts = base_username.replace('_', ' ').replace('.', ' ').split()
        if len(name_parts) > 0:
            first_name = name_parts[0].capitalize()
            if len(name_parts) > 1:
                last_name = ' '.join(name_parts[1:]).capitalize()
    
    print(f"   Creating new user...")
    print(f"   Username: {username}")
    if first_name:
        print(f"   First Name: {first_name}")
    if last_name:
        print(f"   Last Name: {last_name}")
    
    try:
        # Create user with a temporary password (user should set their own password)
        import secrets
        temp_password = secrets.token_urlsafe(16)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            first_name=first_name or '',
            last_name=last_name or '',
            is_active=True,
            is_verified=True,
        )
        
        # Set password to unusable - user should reset password via normal flow
        user.set_unusable_password()
        user.save()
        
        print(f"\n✅ User created successfully!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   ID: {user.id}")
        print(f"   Full Name: {user.get_full_name() or 'N/A'}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Is Verified: {user.is_verified}")
        print(f"\n   The user should now appear in the admin panel!")
        
        return user
        
    except Exception as e:
        print(f"\n❌ Error creating user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python create_user_from_email.py <email> [first_name] [last_name]")
        print("\nExample:")
        print("  python create_user_from_email.py kumargautham28official@gmail.com")
        print("  python create_user_from_email.py user@example.com John Doe")
        sys.exit(1)
    
    email = sys.argv[1]
    first_name = sys.argv[2] if len(sys.argv) > 2 else None
    last_name = sys.argv[3] if len(sys.argv) > 3 else None
    
    create_user_from_email(email, first_name, last_name)

