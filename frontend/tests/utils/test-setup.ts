import { Page } from '@playwright/test'

export interface MockUser {
  id: string
  email: string
  first_name: string
  last_name: string
  role: 'Admin' | 'Manager' | 'Designer'
  organization_id: string
  is_active: boolean
  created_at: string
}

export interface MockOrganization {
  id: string
  name: string
  domain: string
  created_at: string
}

export const mockUsers: MockUser[] = [
  {
    id: '1',
    email: 'admin@example.com',
    first_name: 'John',
    last_name: 'Doe',
    role: 'Admin',
    organization_id: 'org-123',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z'
  },
  {
    id: '2',
    email: 'designer@example.com',
    first_name: 'Jane',
    last_name: 'Smith',
    role: 'Designer',
    organization_id: 'org-123',
    is_active: true,
    created_at: '2024-01-02T00:00:00Z'
  }
]

export const mockOrganization: MockOrganization = {
  id: 'org-123',
  name: 'Test Organization',
  domain: 'test.com',
  created_at: '2024-01-01T00:00:00Z'
}

export async function setupApiMocks(page: Page) {
  // Mock user profile API
  await page.route('**/api/users/profile/', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({
        id: '1',
        email: 'admin@example.com',
        first_name: 'John',
        last_name: 'Doe',
        role: 'Admin',
        organization_id: 'org-123',
        organization: mockOrganization,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      })
    })
  })

  // Mock users list API
  await page.route('**/api/users/', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockUsers)
    })
  })

  // Mock organization API
  await page.route('**/api/organizations/current/', route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mockOrganization)
    })
  })

  // Mock user role update API
  await page.route('**/api/users/*/', route => {
    if (route.request().method() === 'PATCH') {
      const body = route.request().postDataJSON()
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...mockUsers[0],
          role: body.role
        })
      })
    } else if (route.request().method() === 'DELETE') {
      route.fulfill({
        status: 204,
        contentType: 'application/json',
        body: ''
      })
    } else {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockUsers[0])
      })
    }
  })

  // Mock user invite API
  await page.route('**/api/users/invite/', route => {
    route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify({ message: 'User invited successfully' })
    })
  })

  // Mock organization update API
  await page.route('**/api/organizations/current/', route => {
    if (route.request().method() === 'PATCH') {
      const body = route.request().postDataJSON()
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          ...mockOrganization,
          ...body
        })
      })
    } else {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(mockOrganization)
      })
    }
  })
}

export async function setupErrorMocks(page: Page) {
  // Mock API error for error handling tests
  await page.route('**/api/users/profile/', route => {
    route.fulfill({
      status: 500,
      contentType: 'application/json',
      body: JSON.stringify({ error: 'Internal server error' })
    })
  })
}

export async function setupNetworkErrorMocks(page: Page) {
  // Mock network error for error handling tests
  await page.route('**/api/**', route => {
    route.abort('failed')
  })
}

export async function setupSlowApiMocks(page: Page) {
  // Mock slow API response for loading state tests
  await page.route('**/api/users/profile/', route => {
    setTimeout(() => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: '1',
          email: 'admin@example.com',
          first_name: 'John',
          last_name: 'Doe',
          role: 'Admin',
          organization_id: 'org-123',
          organization: mockOrganization,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z'
        })
      })
    }, 1000)
  })
}
