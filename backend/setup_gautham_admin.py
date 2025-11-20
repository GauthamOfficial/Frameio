#!/usr/bin/env python
"""
Setup script to create admin access for superuser Gautham
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import UserProfile
from organizations.models import Organization, OrganizationMember

User = get_user_model()

def setup_gautham_admin():
    print("=== SETTING UP GAUTHAM ADMIN ACCESS ===")
    
    # Check if superuser exists
    try:
        superuser = User.objects.get(username='Gautham')
        print(f"✓ Found superuser: {superuser.username} (Email: {superuser.email})")
        print(f"✓ Is superuser: {superuser.is_superuser}")
        print(f"✓ Is staff: {superuser.is_staff}")
    except User.DoesNotExist:
        print("Creating superuser Gautham...")
        superuser = User.objects.create_superuser(
            username='Gautham',
            email='gautham@framio.com',
            password='imlooser',
            first_name='Gautham',
            last_name='Admin'
        )
        print("✓ Superuser created successfully!")
    
    # Get or create main organization
    try:
        org = Organization.objects.get(slug='framio-main')
        print(f"✓ Found organization: {org.name}")
    except Organization.DoesNotExist:
        print("Creating main organization...")
        org = Organization.objects.create(
            name='Framio Main Organization',
            slug='framio-main',
            description='Main organization for Framio admin',
            subscription_plan='enterprise',
            subscription_status='active',
            ai_generations_limit=10000
        )
        print("✓ Organization created successfully!")
    
    # Create or update user profile
    profile, created = UserProfile.objects.get_or_create(
        user=superuser,
        defaults={
            'current_organization': org,
            'job_title': 'System Administrator',
            'department': 'IT',
            'company_size': '500+'
        }
    )
    if created:
        print("✓ User profile created!")
    else:
        print("✓ User profile already exists!")
    
    # Create admin membership
    membership, created = OrganizationMember.objects.get_or_create(
        organization=org,
        user=superuser,
        defaults={
            'role': 'admin',
            'can_invite_users': True,
            'can_manage_billing': True,
            'can_export_data': True
        }
    )
    if created:
        print("✓ Admin membership created!")
    else:
        print("✓ Admin membership already exists!")
    
    print("\n=== ADMIN ACCESS SETUP COMPLETE ===")
    print(f"Username: {superuser.username}")
    print(f"Email: {superuser.email}")
    print(f"Organization: {org.name}")
    print(f"Role: {membership.role}")
    print(f"Organization ID: {org.id}")
    
    return {
        'user': superuser,
        'organization': org,
        'membership': membership
    }

if __name__ == '__main__':
    setup_gautham_admin()
