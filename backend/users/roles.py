"""
Role-based access control (RBAC) system for Frameio.
Defines roles, permissions, and role-based access patterns.
"""

from rest_framework import permissions
from organizations.models import OrganizationMember
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

# Role hierarchy and permissions
ROLE_HIERARCHY = {
    'admin': ['admin', 'manager', 'designer'],
    'manager': ['manager', 'designer'],
    'designer': ['designer']
}

# Role-specific permissions
ROLE_PERMISSIONS = {
    'admin': {
        'can_manage_users': True,
        'can_manage_organizations': True,
        'can_manage_billing': True,
        'can_export_data': True,
        'can_access_analytics': True,
        'can_manage_ai_services': True,
        'can_manage_templates': True,
        'can_generate_ai': True,
        'can_approve_designs': True,
        'can_manage_projects': True,
    },
    'manager': {
        'can_manage_users': False,
        'can_manage_organizations': False,
        'can_manage_billing': False,
        'can_export_data': True,
        'can_access_analytics': True,
        'can_manage_ai_services': False,
        'can_manage_templates': True,
        'can_generate_ai': True,
        'can_approve_designs': True,
        'can_manage_projects': True,
    },
    'designer': {
        'can_manage_users': False,
        'can_manage_organizations': False,
        'can_manage_billing': False,
        'can_export_data': False,
        'can_access_analytics': False,
        'can_manage_ai_services': False,
        'can_manage_templates': False,
        'can_generate_ai': True,
        'can_approve_designs': False,
        'can_manage_projects': False,
    }
}

# API endpoint permissions
API_PERMISSIONS = {
    # User management endpoints
    '/api/users/': ['admin'],
    '/api/users/invite_user/': ['admin', 'manager'],
    '/api/users/update_role/': ['admin'],
    '/api/users/remove_from_organization/': ['admin'],
    
    # Organization management endpoints
    '/api/organizations/': ['admin'],
    '/api/organizations/invitations/': ['admin', 'manager'],
    
    # AI Services endpoints
    '/api/ai/generation-requests/': ['admin', 'manager', 'designer'],
    '/api/ai/templates/': ['admin', 'manager', 'designer'],
    '/api/ai/analytics/': ['admin', 'manager'],
    '/api/ai/providers/': ['admin', 'manager', 'designer'],
    '/api/ai/quotas/': ['admin', 'manager'],
    
    # AI Generation endpoints
    '/api/ai/poster/generate_poster/': ['admin', 'manager', 'designer'],
    '/api/ai/poster/generate_captions/': ['admin', 'manager', 'designer'],
    '/api/ai/festival-kit/generate_kit/': ['admin', 'manager', 'designer'],
    '/api/ai/catalog/build_catalog/': ['admin', 'manager', 'designer'],
    '/api/ai/background/generate_background/': ['admin', 'manager', 'designer'],
    
    # Project management endpoints
    '/api/projects/': ['admin', 'manager'],
    '/api/projects/approve/': ['admin', 'manager'],
    
    # Analytics endpoints
    '/api/analytics/': ['admin', 'manager'],
    '/api/analytics/usage/': ['admin', 'manager'],
}


class BaseRolePermission(permissions.BasePermission):
    """
    Base permission class for role-based access control.
    """
    
    def __init__(self, allowed_roles=None, required_permission=None):
        self.allowed_roles = allowed_roles or []
        self.required_permission = required_permission
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Get organization context
        organization = getattr(request, 'organization', None)
        if not organization:
            return False
        
        # Get user's role in the organization
        try:
            membership = OrganizationMember.objects.get(
                user=request.user,
                organization=organization,
                is_active=True
            )
            user_role = membership.role
            
            # Set role context in request
            request.role = user_role
            request.organization_membership = membership
            
        except OrganizationMember.DoesNotExist:
            logger.warning(f"User {request.user.id} not found in organization {organization.id}")
            return False
        
        # Check role-based access
        if self.allowed_roles and user_role not in self.allowed_roles:
            return False
        
        # Check specific permission
        if self.required_permission:
            return self._has_permission(user_role, self.required_permission)
        
        return True
    
    def _has_permission(self, role, permission):
        """Check if role has specific permission."""
        role_perms = ROLE_PERMISSIONS.get(role, {})
        return role_perms.get(permission, False)


class IsAdmin(BaseRolePermission):
    """
    Permission class for Admin role only.
    """
    def __init__(self):
        super().__init__(allowed_roles=['admin'])


class IsManager(BaseRolePermission):
    """
    Permission class for Manager role and above (Manager, Admin).
    """
    def __init__(self):
        super().__init__(allowed_roles=['admin', 'manager'])


class IsDesigner(BaseRolePermission):
    """
    Permission class for Designer role and above (Designer, Manager, Admin).
    """
    def __init__(self):
        super().__init__(allowed_roles=['admin', 'manager', 'designer'])


class CanManageUsers(BaseRolePermission):
    """
    Permission class for users who can manage other users.
    """
    def __init__(self):
        super().__init__(required_permission='can_manage_users')


class CanManageBilling(BaseRolePermission):
    """
    Permission class for users who can manage billing.
    """
    def __init__(self):
        super().__init__(required_permission='can_manage_billing')


class CanExportData(BaseRolePermission):
    """
    Permission class for users who can export data.
    """
    def __init__(self):
        super().__init__(required_permission='can_export_data')


class CanAccessAnalytics(BaseRolePermission):
    """
    Permission class for users who can access analytics.
    """
    def __init__(self):
        super().__init__(required_permission='can_access_analytics')


class CanManageAIServices(BaseRolePermission):
    """
    Permission class for users who can manage AI services.
    """
    def __init__(self):
        super().__init__(required_permission='can_manage_ai_services')


class CanGenerateAI(BaseRolePermission):
    """
    Permission class for users who can generate AI content.
    """
    def __init__(self):
        super().__init__(required_permission='can_generate_ai')


class CanApproveDesigns(BaseRolePermission):
    """
    Permission class for users who can approve designs.
    """
    def __init__(self):
        super().__init__(required_permission='can_approve_designs')


class CanManageProjects(BaseRolePermission):
    """
    Permission class for users who can manage projects.
    """
    def __init__(self):
        super().__init__(required_permission='can_manage_projects')


def get_user_role_permissions(user, organization):
    """
    Get all permissions for a user in a specific organization.
    """
    try:
        membership = OrganizationMember.objects.get(
            user=user,
            organization=organization,
            is_active=True
        )
        
        role = membership.role
        permissions = ROLE_PERMISSIONS.get(role, {}).copy()
        
        # Add role information
        permissions.update({
            'role': role,
            'is_admin': role == 'admin',
            'is_manager': role in ['admin', 'manager'],
            'is_designer': role in ['admin', 'manager', 'designer'],
        })
        
        return permissions
        
    except OrganizationMember.DoesNotExist:
        return None


def check_api_permission(user, organization, path, method='GET'):
    """
    Check if user has permission to access a specific API endpoint.
    """
    try:
        membership = OrganizationMember.objects.get(
            user=user,
            organization=organization,
            is_active=True
        )
        
        role = membership.role
        
        # Check if path matches any API permission patterns
        for pattern, allowed_roles in API_PERMISSIONS.items():
            if path.startswith(pattern):
                return role in allowed_roles
        
        # Default: allow access if user is authenticated and in organization
        return True
        
    except OrganizationMember.DoesNotExist:
        return False


def get_role_hierarchy(role):
    """
    Get all roles that the given role can access.
    """
    return ROLE_HIERARCHY.get(role, [])


def can_access_role(current_role, target_role):
    """
    Check if current role can access target role.
    """
    accessible_roles = get_role_hierarchy(current_role)
    return target_role in accessible_roles


def get_role_display_name(role):
    """
    Get display name for role.
    """
    role_names = {
        'admin': 'Administrator',
        'manager': 'Manager',
        'designer': 'Designer'
    }
    return role_names.get(role, role.title())


def get_role_description(role):
    """
    Get description for role.
    """
    descriptions = {
        'admin': 'Full system access including user management, billing, and all features',
        'manager': 'Project management and team oversight with limited administrative access',
        'designer': 'Textile design and AI generation access with project creation capabilities'
    }
    return descriptions.get(role, 'No description available')
