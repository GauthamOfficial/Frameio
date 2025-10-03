"""
Role-based permissions system for multi-tenant organization management.
"""
from rest_framework import permissions
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from organizations.models import OrganizationMember


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission class to check if user is a member of the current organization.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization from request
        organization = getattr(request, 'organization', None)
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
        organization = getattr(request, 'organization', None)
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

