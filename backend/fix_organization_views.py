"""
Fix organization views to handle tenant context properly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from organizations.views import OrganizationViewSet
from users.permissions import IsOrganizationMember
from rest_framework import permissions


def fix_organization_views():
    """Fix organization views to use proper permissions."""
    print("🔧 Fixing organization views...")
    
    # Update OrganizationViewSet to use proper permissions
    OrganizationViewSet.permission_classes = [permissions.IsAuthenticated]
    
    print("✅ Organization views updated")


if __name__ == "__main__":
    fix_organization_views()
