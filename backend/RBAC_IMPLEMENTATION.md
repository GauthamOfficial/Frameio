# RBAC (Role-Based Access Control) Implementation

This document describes the implementation of Role-Based Access Control (RBAC) for the Frameio project, separating Admin Mode and User Mode properly following RBAC best practices.

## Overview

The RBAC system defines three main roles with hierarchical permissions:
- **Admin**: Full system access including user management, billing, and all features
- **Manager**: Project management and team oversight with limited administrative access  
- **Designer**: Textile design and AI generation access with project creation capabilities

## Role Definitions

### Admin Role
- **Full system access** including user management, billing, and all features
- **Permissions**:
  - Can manage users (invite, remove, change roles)
  - Can manage organizations (create, update, delete)
  - Can manage billing and subscription settings
  - Can export data and access analytics
  - Can manage AI services and templates
  - Can generate AI content
  - Can approve designs
  - Can manage projects

### Manager Role
- **Project management and team oversight** with limited administrative access
- **Permissions**:
  - Cannot manage users or organizations
  - Cannot manage billing
  - Can export data and access analytics
  - Cannot manage AI services
  - Can manage templates
  - Can generate AI content
  - Can approve designs
  - Can manage projects

### Designer Role
- **Textile design and AI generation** access with project creation capabilities
- **Permissions**:
  - Cannot manage users, organizations, or billing
  - Cannot export data or access analytics
  - Cannot manage AI services or templates
  - Can generate AI content
  - Cannot approve designs
  - Cannot manage projects

## API Endpoint Permissions

### User Management Endpoints
- `/api/users/` → **Admin only**
- `/api/users/invite_user/` → **Admin + Manager**
- `/api/users/update_role/` → **Admin only**
- `/api/users/remove_from_organization/` → **Admin only**

### Organization Management Endpoints
- `/api/organizations/` → **Admin only**
- `/api/organizations/invitations/` → **Admin + Manager**

### AI Services Endpoints
- `/api/ai/generation-requests/` → **Admin + Manager + Designer**
- `/api/ai/templates/` → **Admin + Manager + Designer**
- `/api/ai/analytics/` → **Admin + Manager**
- `/api/ai/providers/` → **Admin + Manager + Designer**
- `/api/ai/quotas/` → **Admin + Manager**

### AI Generation Endpoints
- `/api/ai/poster/generate_poster/` → **Admin + Manager + Designer**
- `/api/ai/poster/generate_captions/` → **Admin + Manager + Designer**
- `/api/ai/festival-kit/generate_kit/` → **Admin + Manager + Designer**
- `/api/ai/catalog/build_catalog/` → **Admin + Manager + Designer**
- `/api/ai/background/generate_background/` → **Admin + Manager + Designer**

### Project Management Endpoints
- `/api/projects/` → **Admin + Manager**
- `/api/projects/approve/` → **Admin + Manager**

### Analytics Endpoints
- `/api/analytics/` → **Admin + Manager**
- `/api/analytics/usage/` → **Admin + Manager**

## Implementation Details

### 1. Role System (`users/roles.py`)

The core RBAC system is implemented in `users/roles.py` with:

- **Role hierarchy definition**: Admin > Manager > Designer
- **Permission mapping**: Each role has specific permissions
- **API endpoint protection**: Endpoints are mapped to allowed roles
- **Permission classes**: Custom DRF permission classes for each role

### 2. Permission Classes

#### Base Classes
- `BaseRolePermission`: Base class for all role-based permissions
- `IsAdmin`: Admin role only
- `IsManager`: Manager role and above (Manager, Admin)
- `IsDesigner`: Designer role and above (Designer, Manager, Admin)

#### Specific Permission Classes
- `CanManageUsers`: Users who can manage other users
- `CanManageBilling`: Users who can manage billing
- `CanExportData`: Users who can export data
- `CanAccessAnalytics`: Users who can access analytics
- `CanManageAIServices`: Users who can manage AI services
- `CanGenerateAI`: Users who can generate AI content
- `CanApproveDesigns`: Users who can approve designs
- `CanManageProjects`: Users who can manage projects

### 3. Middleware Integration

#### Organization Middleware (`organizations/middleware.py`)
- Extracts user role from organization membership
- Sets role context in request object (`request.role`)
- Sets role permissions context (`request.role_permissions`)

#### AI Services Middleware (`ai_services/middleware.py`)
- Implements role-based rate limiting
- Different rate limits for different roles:
  - **Admin**: 100 requests/minute, 1000/hour
  - **Manager**: 50 requests/minute, 500/hour  
  - **Designer**: 10 requests/minute, 100/hour

### 4. API Protection

All API endpoints are protected with appropriate permission classes:

```python
# Example: AI Generation endpoints
class AIGenerationRequestViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, CanGenerateAI]

# Example: Analytics endpoints  
class AIAnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated, CanAccessAnalytics]
```

### 5. Authentication Endpoints

New authentication endpoints provide role context:

- `GET /api/auth/me/` - Get current user with role information
- `GET /api/auth/role_info/` - Get detailed role information

Response includes:
```json
{
  "user": { ... },
  "organization": { ... },
  "role": "admin",
  "permissions": {
    "can_manage_users": true,
    "can_manage_billing": true,
    "can_export_data": true,
    "can_access_analytics": true,
    "can_manage_ai_services": true,
    "can_generate_ai": true,
    "can_approve_designs": true,
    "can_manage_projects": true
  }
}
```

## Frontend Integration

The backend provides role information that the frontend can use to:

1. **Load correct UI mode**:
   - Admin Dashboard for Admin users
   - Manager Dashboard for Manager users  
   - Designer Dashboard for Designer users

2. **Show/hide features** based on permissions:
   - User management features for Admin only
   - Analytics features for Admin + Manager
   - AI generation features for all roles

3. **Implement role switching** (if needed):
   - Admin and Manager users can switch to Designer mode
   - Designer users cannot switch modes

## Testing

Run the RBAC test script to verify the implementation:

```bash
cd backend
python test_rbac_system.py
```

This will:
- Create test users with different roles
- Verify role permissions
- Test API endpoint access
- Check middleware integration

## Migration Notes

### Backward Compatibility
- Existing permission classes are aliased to new RBAC classes
- `IsOrganizationMember` → `IsDesigner`
- `IsOrganizationAdmin` → `IsAdmin`
- `IsOrganizationManager` → `IsManager`

### Database Changes
- No database migrations required
- Uses existing `OrganizationMember.role` field
- Role values: 'admin', 'manager', 'designer'

### Middleware Order
Ensure middleware is configured in the correct order:
1. `TenantMiddleware` - Sets organization context
2. `OrganizationPermissionMiddleware` - Sets role context
3. `RateLimitMiddleware` - Applies role-based rate limiting

## Security Considerations

1. **Role validation**: All role checks are performed server-side
2. **Permission inheritance**: Higher roles inherit permissions from lower roles
3. **Rate limiting**: Different limits for different roles prevent abuse
4. **API protection**: All endpoints are protected with appropriate permissions
5. **Context isolation**: Users can only access their organization's data

## Troubleshooting

### Common Issues

1. **Permission denied errors**: Check if user has correct role in organization
2. **Rate limit exceeded**: Check role-based rate limits
3. **Missing role context**: Ensure middleware is properly configured
4. **API access denied**: Verify endpoint permissions match user role

### Debug Information

Check request context:
```python
# In views or middleware
print(f"User role: {request.role}")
print(f"Role permissions: {request.role_permissions}")
print(f"Organization: {request.organization}")
```

## Future Enhancements

1. **Custom roles**: Allow organizations to define custom roles
2. **Permission inheritance**: More granular permission inheritance
3. **Role switching**: Allow users to switch between roles
4. **Audit logging**: Log role-based actions for security
5. **Role templates**: Predefined role templates for different use cases
