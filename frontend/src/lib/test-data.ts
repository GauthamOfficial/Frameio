// Utility functions for setting test data during development

export const setTestUserData = (role: 'Admin' | 'Manager' | 'Designer' = 'Designer') => {
  if (typeof window === 'undefined') return

  const permissions = {
    Admin: ['manage_users', 'manage_organization', 'view_billing', 'manage_designs', 'view_analytics', 'manage_templates'],
    Manager: ['manage_designs', 'view_analytics', 'manage_templates', 'moderate_users'],
    Designer: ['manage_designs', 'view_templates', 'view_analytics']
  }

  localStorage.setItem('user-role', role)
  localStorage.setItem('organization-id', 'test-org-123')
  localStorage.setItem('organization-name', 'Test Organization')
  localStorage.setItem('user-permissions', JSON.stringify(permissions[role]))

  console.log(`Test data set for ${role} role with permissions:`, permissions[role])
}

export const clearTestData = () => {
  if (typeof window === 'undefined') return

  localStorage.removeItem('user-role')
  localStorage.removeItem('organization-id')
  localStorage.removeItem('organization-name')
  localStorage.removeItem('user-permissions')

  console.log('Test data cleared')
}

// Make functions available globally for console access
if (typeof window !== 'undefined') {
  const typedWindow = window as Window & { setTestUserData?: typeof setTestUserData; clearTestData?: typeof clearTestData }
  typedWindow.setTestUserData = setTestUserData
  typedWindow.clearTestData = clearTestData
}
