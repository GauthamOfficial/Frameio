"""
Role-based permissions system for multi-tenant organization management.
"""
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from organizations.models import OrganizationMember
import os


class IsVerified(permissions.BasePermission):
    """
    Permission class that requires the user to have verified their email.
    """
    message = "Please verify your email address to access this feature."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_verified:
            raise PermissionDenied(
                detail="Your email address must be verified to access this feature. Please check your email for the verification link.",
                code="email_not_verified"
            )
        
        return True


def get_organization_from_request(request):
    """
    Helper function to get organization from request with fallbacks for testing.
    """
    # Get organization from request (set by TenantMiddleware)
    organization = getattr(request, 'organization', None)
    if not organization:
        # For testing, try to get organization from authenticated user
        if hasattr(request, 'user') and request.user.is_authenticated:
            organization = request.user.current_organization
            if not organization:
                # Get first organization the user belongs to
                memberships = request.user.organization_memberships.filter(is_active=True)
                if memberships.exists():
                    organization = memberships.first().organization
    return organization


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission class to check if user is a member of the current organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = get_organization_from_request(request)
        if not organization:
            return False
        
        # Check if user is a member of the organization
        return OrganizationMember.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).exists()


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission class to check if user is an admin of the current organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = get_organization_from_request(request)
        if not organization:
            return False
        
        # Check if user is an admin of the organization
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.role == 'admin'
        except OrganizationMember.DoesNotExist:
            return False


class IsOrganizationManager(permissions.BasePermission):
    """
    Permission class to check if user is a manager or admin of the current organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user is a manager or admin of the organization
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.role in ['admin', 'manager']
        except OrganizationMember.DoesNotExist:
            return False


class IsOrganizationDesigner(permissions.BasePermission):
    """
    Permission class to check if user is a designer, manager, or admin of the current organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user has any role in the organization
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.role in ['admin', 'manager', 'designer']
        except OrganizationMember.DoesNotExist:
            return False


class CanManageUsers(permissions.BasePermission):
    """
    Permission class to check if user can manage other users in the organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            # For testing, try to get organization from authenticated user
            organization = request.user.current_organization
            if not organization:
                # Get first organization the user belongs to
                memberships = request.user.organization_memberships.filter(is_active=True)
                if memberships.exists():
                    organization = memberships.first().organization
        
        if not organization:
            return False
        
        # Check if user can manage users
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.can_invite_users or membership.role == 'admin'
        except OrganizationMember.DoesNotExist:
            return False


class CanManageBilling(permissions.BasePermission):
    """
    Permission class to check if user can manage billing for the organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user can manage billing
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.can_manage_billing or membership.role == 'admin'
        except OrganizationMember.DoesNotExist:
            return False


class CanExportData(permissions.BasePermission):
    """
    Permission class to check if user can export data from the organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user can export data
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.can_export_data or membership.role == 'admin'
        except OrganizationMember.DoesNotExist:
            return False


class RoleBasedPermission(permissions.BasePermission):
    """
    Generic role-based permission class that can be configured for different roles.
    """
    
    def __init__(self, allowed_roles=None):
        self.allowed_roles = allowed_roles or []
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Check if user has one of the allowed roles
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.role in self.allowed_roles
        except OrganizationMember.DoesNotExist:
            return False


def get_user_organization_permissions(user, organization):
    """
    Get all permissions for a user in a specific organization.
    """
    try:
        membership = OrganizationMember.objects.get(
            user=user,
            organization=organization,
            is_active=True
        )
        
        permissions = {
            'role': membership.role,
            'can_invite_users': membership.can_invite_users,
            'can_manage_billing': membership.can_manage_billing,
            'can_export_data': membership.can_export_data,
            'is_admin': membership.role == 'admin',
            'is_manager': membership.role in ['admin', 'manager'],
            'is_designer': membership.role in ['admin', 'manager', 'designer'],
        }
        
        return permissions
    except OrganizationMember.DoesNotExist:
        return None


class IsAdminRequest(permissions.BasePermission):
    """
    Permission class to allow admin panel requests via X-Admin-Request header.
    This bypasses normal authentication for admin operations.
    """
    
    def has_permission(self, request, view):
        # Check for admin request header
        admin_header = request.META.get('HTTP_X_ADMIN_REQUEST', '').lower()
        admin_username = request.META.get('HTTP_X_ADMIN_USERNAME', '')
        
        if admin_header == 'true' and admin_username:
            # Verify admin username matches configured admin
            expected_admin = os.getenv('ADMIN_USERNAME', 'tsg_admin')
            if admin_username == expected_admin:
                # Set a flag on the request to indicate this is an admin request
                request._admin_request = True
                return True
        
        # Fall back to normal authentication
        return False


class IsAuthenticatedOrAdmin(permissions.BasePermission):
    """
    Permission class that allows either authenticated users OR admin requests.
    """
    
    def has_permission(self, request, view):
        # Check if it's an admin request first
        admin_header = request.META.get('HTTP_X_ADMIN_REQUEST', '').lower()
        admin_username = request.META.get('HTTP_X_ADMIN_USERNAME', '')
        
        if admin_header == 'true' and admin_username:
            expected_admin = os.getenv('ADMIN_USERNAME', 'tsg_admin')
            if admin_username == expected_admin:
                request._admin_request = True
                return True
        
        # Otherwise, require authentication
        return request.user and request.user.is_authenticated


class IsOrganizationMemberOrAdmin(permissions.BasePermission):
    """
    Permission class that allows organization members OR admin requests.
    """
    
    def has_permission(self, request, view):
        # Check if it's an admin request first
        if getattr(request, '_admin_request', False):
            return True
        
        # Otherwise, check organization membership
        if not request.user or not request.user.is_authenticated:
            return False
        
        organization = get_organization_from_request(request)
        if not organization:
            return False
        
        return OrganizationMember.objects.filter(
            user=request.user,
            organization=organization,
            is_active=True
        ).exists()


class CanManageUsersOrAdmin(permissions.BasePermission):
    """
    Permission class that allows users with manage permissions OR admin requests.
    """
    
    def has_permission(self, request, view):
        # Check if it's an admin request first
        if getattr(request, '_admin_request', False):
            return True
        
        # Otherwise, check normal permissions
        if not request.user or not request.user.is_authenticated:
            return False
        
        organization = get_organization_from_request(request)
        if not organization:
            return False
        
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            return membership.can_invite_users or membership.role == 'admin'
        except OrganizationMember.DoesNotExist:
            return False


def create_role_permissions():
    """
    Create default permissions for each role.
    This should be called during migration or setup.
    """
    # Get or create content types
    organization_ct = ContentType.objects.get_for_model(OrganizationMember)
    
    # Define permissions for each role
    role_permissions = {
        'admin': [
            'add_organizationmember',
            'change_organizationmember',
            'delete_organizationmember',
            'view_organizationmember',
            'add_organizationinvitation',
            'change_organizationinvitation',
            'delete_organizationinvitation',
            'view_organizationinvitation',
        ],
        'manager': [
            'view_organizationmember',
            'add_organizationinvitation',
            'view_organizationinvitation',
        ],
        'designer': [
            'view_organizationmember',
        ],
    }
    
    # Create permissions if they don't exist
    for role, perm_codenames in role_permissions.items():
        for codename in perm_codenames:
            permission, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=organization_ct,
                defaults={'name': f'Can {codename.replace("_", " ")}'}
            )
    
    return True

