#!/usr/bin/env python
"""
Script to create a test user for development
Run this to fix the "Permission denied" error
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

User = get_user_model()

def create_test_user():
    """Create a test user for development"""
    
    # Check if user already exists
    if User.objects.exists():
        user = User.objects.first()
        print(f"[OK] User already exists: {user.email} (ID: {user.id})")
        print(f"   Username: {user.username}")
        return user
    
    # Create a new test user
    print("[INFO] No users found. Creating test user...")
    
    try:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        print(f"[OK] Created test user successfully!")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   ID: {user.id}")
        print(f"\n   You can now use the app without permission errors!")
        return user
    except Exception as e:
        print(f"[ERROR] Error creating user: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_test_user()

