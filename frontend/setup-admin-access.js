// Quick setup script for admin access in development
// Run this in your browser console to get admin access

console.log('Setting up admin access...');

// Set admin role and permissions
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
localStorage.setItem('organization-id', '0a4e8956-b626-4ac5-b082-b13febeb5bfe');
localStorage.setItem('organization-name', 'Test Organization');
localStorage.setItem('dev-user-id', 'youradmin@framio.com');
localStorage.setItem('dev-org-id', '0a4e8956-b626-4ac5-b082-b13febeb5bfe');

console.log('Admin access configured!');
console.log('Now refresh the page and try accessing /admin');

// Verify the setup
console.log('Current localStorage values:');
console.log('user-role:', localStorage.getItem('user-role'));
console.log('user-permissions:', localStorage.getItem('user-permissions'));
console.log('organization-id:', localStorage.getItem('organization-id'));
