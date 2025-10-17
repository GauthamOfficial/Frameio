// Setup script for Gautham's admin access
// Run this in your browser console to get admin access as Gautham

console.log('Setting up Gautham admin access...');

// Set admin role and permissions for Gautham
localStorage.setItem('user-role', 'Admin');
localStorage.setItem('user-permissions', JSON.stringify([
  'admin_access',
  'manage_users',
  'manage_organizations',
  'manage_billing',
  'export_data',
  'manage_ai_services',
  'manage_designs',
  'view_templates',
  'view_analytics'
]));

// Set organization context for Gautham's organization
localStorage.setItem('organization-id', '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb');
localStorage.setItem('organization-name', 'Framio Main Organization');
localStorage.setItem('organization-slug', 'framio-main');

// Set user context
localStorage.setItem('dev-user-id', 'Gautham');
localStorage.setItem('dev-org-id', '4fc5b2aa-031b-46be-a723-0e5d5b0f7ddb');

// Set authentication context
localStorage.setItem('is-authenticated', 'true');
localStorage.setItem('user-email', 'gautham@framio.com');
localStorage.setItem('user-name', 'Gautham Admin');

console.log('✅ Gautham admin access configured!');
console.log('Now refresh the page and try accessing /admin');

// Verify the setup
console.log('Current localStorage values:');
console.log('user-role:', localStorage.getItem('user-role'));
console.log('user-permissions:', localStorage.getItem('user-permissions'));
console.log('organization-id:', localStorage.getItem('organization-id'));
console.log('organization-name:', localStorage.getItem('organization-name'));
console.log('dev-user-id:', localStorage.getItem('dev-user-id'));
