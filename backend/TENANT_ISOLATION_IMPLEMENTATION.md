# Tenant Isolation and Role-Based Permissions Implementation

## Overview

This document describes the implementation of organization-based tenant isolation and role-based permissions system for the Frameio backend project.

## Features Implemented

### 1. Organization-Based Tenant Isolation

#### Models
- **Organization**: Core tenant model with subscription management
- **OrganizationMember**: Manages user membership and roles within organizations
- **OrganizationInvitation**: Handles user invitations to organizations
- **UserProfile**: Extended user profile with organization context

#### Key Features
- Each user belongs to exactly one organization (primary)
- Data (designs, catalogs, templates) is scoped to the tenant
- Automatic organization assignment via `TenantScopedModel`
- Thread-local organization context via middleware

### 2. User Roles and Permissions System

#### Roles
- **Admin**: Full control (organization settings, users, billing, designs)
- **Manager**: Manage designs and catalogs, moderate users (no billing)
- **Designer**: Can only create/edit designs

#### Permission Classes
- `IsOrganizationMember`: Basic organization membership
- `IsOrganizationAdmin`: Admin-level access
- `IsOrganizationManager`: Manager or admin access
- `CanManageUsers`: User management permissions
- `CanManageBilling`: Billing management permissions
- `CanExportData`: Data export permissions

### 3. User Management APIs

#### Endpoints
- `GET /api/users/` - List organization users
- `POST /api/users/invite_user/` - Invite new user
- `POST /api/users/{id}/update_role/` - Update user role
- `POST /api/users/{id}/remove_from_organization/` - Remove user
- `GET /api/users/permissions/` - Get user permissions

#### Features
- All APIs are tenant-scoped
- Role-based access control
- Invitation system with expiration
- Permission validation

### 4. Database Migrations and Seeding

#### Management Commands
- `python manage.py seed_roles` - Seed default roles and permissions
- `--create-sample-org` - Create sample organization
- `--create-sample-users` - Create sample users

#### Migration Strategy
- Existing models updated with tenant isolation
- New models for organization management
- Proper indexing for performance

### 5. Tenant-Scoped Data Access Patterns

#### Mixins
- `TenantScopedModel`: Abstract base for tenant-scoped models
- `TenantScopedManager`: Manager with automatic organization filtering
- `TenantScopedViewSetMixin`: ViewSet mixin for tenant scoping
- `TenantScopedSerializerMixin`: Serializer mixin for organization context

#### Middleware
- `TenantMiddleware`: Sets organization context from request
- `OrganizationPermissionMiddleware`: Checks organization permissions

## Technical Implementation

### Database Schema

```sql
-- Organizations table
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    subscription_plan VARCHAR(50) DEFAULT 'free',
    subscription_status VARCHAR(50) DEFAULT 'active',
    ai_generations_used INTEGER DEFAULT 0,
    ai_generations_limit INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Organization members table
CREATE TABLE organization_members (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20) DEFAULT 'designer',
    is_active BOOLEAN DEFAULT TRUE,
    can_invite_users BOOLEAN DEFAULT FALSE,
    can_manage_billing BOOLEAN DEFAULT FALSE,
    can_export_data BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(organization_id, user_id)
);

-- Organization invitations table
CREATE TABLE organization_invitations (
    id UUID PRIMARY KEY,
    organization_id UUID REFERENCES organizations(id),
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    invited_by_id UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'pending',
    token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    responded_at TIMESTAMP,
    UNIQUE(organization_id, email)
);
```

### API Endpoints

#### Organization Management
```
GET    /api/organizations/                    # List user's organizations
POST   /api/organizations/                    # Create organization
GET    /api/organizations/{id}/               # Get organization details
PATCH  /api/organizations/{id}/               # Update organization
DELETE /api/organizations/{id}/               # Delete organization
GET    /api/organizations/{id}/members/       # Get organization members
POST   /api/organizations/{id}/invite_member/ # Invite member
GET    /api/organizations/{id}/invitations/   # Get invitations
GET    /api/organizations/{id}/usage/         # Get usage statistics
```

#### User Management
```
GET    /api/users/                            # List organization users
GET    /api/users/{id}/                       # Get user details
PATCH  /api/users/{id}/                       # Update user profile
POST   /api/users/invite_user/                # Invite new user
POST   /api/users/{id}/update_role/           # Update user role
POST   /api/users/{id}/remove_from_organization/ # Remove user
GET    /api/users/permissions/                # Get user permissions
GET    /api/users/invitations/                # Get pending invitations
```

#### Invitation Management
```
GET    /api/invitations/                      # List invitations
POST   /api/invitations/{id}/accept/          # Accept invitation
POST   /api/invitations/{id}/decline/         # Decline invitation
DELETE /api/invitations/{id}/                 # Cancel invitation
```

### Security Features

#### Authentication
- Clerk integration for user authentication
- JWT token validation
- Session management

#### Authorization
- Role-based access control
- Organization-scoped permissions
- API endpoint protection

#### Data Isolation
- Automatic organization filtering
- Cross-tenant access prevention
- Permission validation

### Testing

#### Test Coverage
- Tenant isolation tests
- Role-based permission tests
- API endpoint tests
- Cross-tenant access prevention tests

#### Test Files
- `users/test_tenant_isolation.py` - User management tests
- `organizations/test_organization_management.py` - Organization tests
- `users/test_permissions.py` - Permission tests
- `organizations/test_tenant_isolation.py` - Tenant isolation tests

#### Running Tests
```bash
# Run all tenant tests
python run_tenant_tests.py

# Run specific test modules
python manage.py test users.test_tenant_isolation
python manage.py test organizations.test_organization_management
```

## Usage Examples

### Creating an Organization
```python
# Create organization
org = Organization.objects.create(
    name='My Company',
    slug='my-company',
    description='Our design agency',
    industry='Creative'
)

# Make user the owner
OrganizationMember.objects.create(
    organization=org,
    user=request.user,
    role='owner',
    can_invite_users=True,
    can_manage_billing=True,
    can_export_data=True
)
```

### Inviting a User
```python
# Create invitation
invitation = OrganizationInvitation.objects.create(
    organization=org,
    email='newuser@example.com',
    role='designer',
    invited_by=request.user,
    token=str(uuid.uuid4()),
    expires_at=timezone.now() + timedelta(days=7)
)
```

### Checking Permissions
```python
# Check if user can manage users
if membership.can_invite_users:
    # Allow user management actions
    pass

# Check role-based permissions
if membership.role in ['admin', 'manager']:
    # Allow design management
    pass
```

### Tenant-Scoped Queries
```python
# Automatic organization filtering
designs = Design.objects.all()  # Only returns designs for current organization

# Manual organization filtering
designs = Design.objects.filter(organization=org)

# Cross-organization queries (use with caution)
all_designs = Design.objects.all_organizations()
```

## Configuration

### Settings
```python
# Multi-tenancy settings
TENANT_MODEL = 'organizations.Organization'
AUTH_USER_MODEL = 'users.User'

# Clerk configuration
CLERK_PUBLISHABLE_KEY = os.getenv('CLERK_PUBLISHABLE_KEY')
CLERK_SECRET_KEY = os.getenv('CLERK_SECRET_KEY')
```

### Middleware Order
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'organizations.middleware.TenantMiddleware',  # Tenant context
    'organizations.middleware.OrganizationPermissionMiddleware',  # Permissions
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

## Deployment Considerations

### Database
- Ensure proper indexing on organization_id fields
- Consider partitioning for large datasets
- Monitor query performance

### Security
- Validate organization context in all API endpoints
- Implement rate limiting per organization
- Audit cross-tenant access attempts

### Performance
- Use database connection pooling
- Implement caching for organization data
- Monitor tenant-specific resource usage

## Future Enhancements

### Planned Features
- Organization-level settings and preferences
- Advanced role customization
- Bulk user management operations
- Organization analytics and reporting
- Multi-organization user support

### Scalability
- Database sharding by organization
- Caching layer for organization data
- Background job processing per tenant
- API rate limiting per organization

## Troubleshooting

### Common Issues
1. **Organization context not set**: Check middleware order and request headers
2. **Permission denied**: Verify user role and organization membership
3. **Cross-tenant data access**: Ensure proper queryset filtering
4. **Invitation not working**: Check token expiration and email delivery

### Debugging
```python
# Check current organization context
from organizations.middleware import get_current_organization
org = get_current_organization()

# Check user permissions
from users.permissions import get_user_organization_permissions
perms = get_user_organization_permissions(user, org)

# Debug tenant filtering
from organizations.mixins import get_tenant_queryset
queryset = get_tenant_queryset(Design, org)
```

## Conclusion

The tenant isolation and role-based permissions system provides a robust foundation for multi-tenant SaaS applications. The implementation ensures data security, proper access control, and scalable architecture for future growth.
