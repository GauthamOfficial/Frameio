# Role-Based Frontend Structure

This document describes the new role-based frontend structure that separates User and Admin functionality into distinct panels.

## Structure Overview

```
src/
├── user/                          # User-specific components and pages
│   ├── UserDashboard.tsx         # Main user dashboard wrapper
│   ├── UserDashboardStructure.tsx # User dashboard layout structure
│   ├── UserSidebar.tsx           # User navigation sidebar
│   └── UserOverview.tsx          # User dashboard overview page
├── admin/                         # Admin-specific components and pages
│   ├── AdminDashboard.tsx        # Main admin dashboard wrapper
│   ├── AdminDashboardStructure.tsx # Admin dashboard layout structure
│   ├── AdminSidebar.tsx          # Admin navigation sidebar
│   └── AdminOverview.tsx         # Admin dashboard overview page
├── components/
│   ├── auth/
│   │   ├── role-based-route.tsx  # Role-based route protection
│   │   └── panel-redirect.tsx    # Automatic panel redirection
│   └── navigation/
│       └── panel-navigation.tsx  # Panel-specific navigation
└── app/
    ├── user/                      # User routes (/user/*)
    │   ├── layout.tsx            # User layout with role protection
    │   ├── page.tsx              # User dashboard home
    │   ├── poster-generator/     # User features
    │   ├── catalog-builder/
    │   └── settings/
    └── admin/                     # Admin routes (/admin/*)
        ├── layout.tsx            # Admin layout with role protection
        ├── page.tsx              # Admin dashboard home
        ├── users/                # Admin features
        └── settings/
```

## Role-Based Access Control

### User Roles
- **User/Member**: Access to `/user/*` routes only
- **Admin**: Access to `/admin/*` routes only

### Route Protection
- `RoleBasedRoute`: Protects routes based on user role
- `PanelRedirect`: Automatically redirects users to their appropriate panel
- Unauthorized access attempts redirect to the correct panel

### Navigation
- Users see only "User Panel" link
- Admins see only "Admin Panel" link
- No cross-panel navigation for unauthorized users

## Key Features

### User Panel (`/user/*`)
- AI Poster Generator
- Catalog Builder
- Branding Kit
- Social Media Posts
- Scheduler
- Templates Library
- Analytics
- User Settings

### Admin Panel (`/admin/*`)
- User Management
- Organization Management
- Billing Management
- System Analytics
- User Roles
- Database Management
- System Settings

## Implementation Details

### Role-Based Route Protection
```tsx
<RoleBasedRoute allowedRoles={['Admin']} redirectTo="/user">
  <AdminDashboard>
    {children}
  </AdminDashboard>
</RoleBasedRoute>
```

### Automatic Panel Redirection
```tsx
<PanelRedirect>
  <div>Redirecting to your panel...</div>
</PanelRedirect>
```

### Panel-Specific Navigation
- User sidebar shows only user features
- Admin sidebar shows only admin features
- Role-based filtering of navigation items

## Security Features

1. **Route Protection**: Each panel is protected by role-based access control
2. **Automatic Redirection**: Users are automatically redirected to their appropriate panel
3. **Navigation Filtering**: Navigation items are filtered based on user permissions
4. **No Cross-Panel Access**: Users cannot access the other panel's functionality

## Migration Notes

- Existing `/dashboard/*` routes now redirect to appropriate panels
- Old dashboard components are preserved but redirected
- New structure maintains all existing functionality while adding role separation
- Backward compatibility maintained through redirects

## Usage

1. **For Users**: Navigate to `/user` to access user features
2. **For Admins**: Navigate to `/admin` to access admin features
3. **Automatic**: Visit `/` to be automatically redirected to your panel
4. **Security**: Unauthorized access attempts are automatically redirected
