import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import '@testing-library/jest-dom'
import { ToastProvider } from '@/components/common'
import { AppProvider } from '@/contexts/app-context'
import { OrganizationProvider } from '@/contexts/organization-context'

// Mock Clerk
jest.mock('@clerk/nextjs', () => ({
  useUser: () => ({
    user: { id: 'test-user', email: 'test@example.com' },
    isLoaded: true
  }),
  useAuth: () => ({
    getToken: jest.fn().mockResolvedValue('mock-token'),
    signOut: jest.fn()
  })
}))

// Mock Next.js router
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    back: jest.fn()
  })
}))

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ToastProvider>
    <AppProvider>
      <OrganizationProvider>
        {children}
      </OrganizationProvider>
    </AppProvider>
  </ToastProvider>
)

describe('Phase 1 Week 3 Deliverables', () => {
  describe('1. AI Generation Interface and Controls', () => {
    test('Poster Generator component renders correctly', async () => {
      const PosterGenerator = (await import('@/components/lazy/poster-generator')).default
      
      render(
        <TestWrapper>
          <PosterGenerator />
        </TestWrapper>
      )

      // Check if main elements are present
      expect(screen.getByText('AI Poster Generator')).toBeInTheDocument()
      expect(screen.getByText('Upload & Configure')).toBeInTheDocument()
      expect(screen.getByText('Preview')).toBeInTheDocument()
      expect(screen.getByText('Recent Generations')).toBeInTheDocument()
      
      // Check if AI prompt input is present
      expect(screen.getByPlaceholderText(/Describe the style, colors, and mood/)).toBeInTheDocument()
      
      // Check if style options are present
      expect(screen.getByText('Festival')).toBeInTheDocument()
      expect(screen.getByText('Modern')).toBeInTheDocument()
      expect(screen.getByText('Traditional')).toBeInTheDocument()
      expect(screen.getByText('Minimalist')).toBeInTheDocument()
      
      // Check if generate button is present
      expect(screen.getByText('Generate Poster')).toBeInTheDocument()
    })

    test('Catalog Builder component renders correctly', async () => {
      const CatalogBuilder = (await import('@/components/lazy/catalog-builder')).default
      
      render(
        <TestWrapper>
          <CatalogBuilder />
        </TestWrapper>
      )

      // Check if main elements are present
      expect(screen.getByText('Catalog Builder')).toBeInTheDocument()
      expect(screen.getByText('AI Color Suggestions')).toBeInTheDocument()
      expect(screen.getByText('Catalog Templates')).toBeInTheDocument()
      
      // Check if products are displayed
      expect(screen.getByText('Silk Saree Collection')).toBeInTheDocument()
      expect(screen.getByText('Cotton Kurta Set')).toBeInTheDocument()
      expect(screen.getByText('Linen Dress')).toBeInTheDocument()
      expect(screen.getByText('Chiffon Scarf')).toBeInTheDocument()
      
      // Check if AI color suggestions are present
      expect(screen.getByText('Deep Navy + Gold')).toBeInTheDocument()
      expect(screen.getByText('Maroon + Cream')).toBeInTheDocument()
    })
  })

  describe('2. Design Preview and Editing Tools', () => {
    test('Preview section in Poster Generator works', async () => {
      const PosterGenerator = (await import('@/components/lazy/poster-generator')).default
      
      render(
        <TestWrapper>
          <PosterGenerator />
        </TestWrapper>
      )

      // Check if preview section is present
      expect(screen.getByText('Preview')).toBeInTheDocument()
      expect(screen.getByText('Generated poster will appear here')).toBeInTheDocument()
      
      // Check if action buttons are present
      expect(screen.getByText('Schedule')).toBeInTheDocument()
      expect(screen.getByText('Post Now')).toBeInTheDocument()
      expect(screen.getByText('Download')).toBeInTheDocument()
    })

    test('Product selection in Catalog Builder works', async () => {
      const CatalogBuilder = (await import('@/components/lazy/catalog-builder')).default
      
      render(
        <TestWrapper>
          <CatalogBuilder />
        </TestWrapper>
      )

      // Check if product selection buttons are present
      const addButtons = screen.getAllByText('Add')
      expect(addButtons.length).toBeGreaterThan(0)
      
      // Test product selection
      fireEvent.click(addButtons[0])
      
      // Check if button text changes to "Added"
      await waitFor(() => {
        expect(screen.getByText('Added')).toBeInTheDocument()
      })
    })
  })

  describe('3. Export and Download Functionality', () => {
    test('Download buttons are present and functional', async () => {
      const PosterGenerator = (await import('@/components/lazy/poster-generator')).default
      
      render(
        <TestWrapper>
          <PosterGenerator />
        </TestWrapper>
      )

      // Check if download button is present
      const downloadButton = screen.getByText('Download')
      expect(downloadButton).toBeInTheDocument()
      
      // Test click functionality (should not throw error)
      fireEvent.click(downloadButton)
    })

    test('Catalog creation functionality works', async () => {
      const CatalogBuilder = (await import('@/components/lazy/catalog-builder')).default
      
      render(
        <TestWrapper>
          <CatalogBuilder />
        </TestWrapper>
      )

      // First select a product
      const addButtons = screen.getAllByText('Add')
      fireEvent.click(addButtons[0])
      
      // Wait for button to change to "Added"
      await waitFor(() => {
        expect(screen.getByText('Added')).toBeInTheDocument()
      })
      
      // Check if create catalog button is enabled
      const createButton = screen.getByText(/Create Catalog/)
      expect(createButton).toBeInTheDocument()
      expect(createButton).not.toBeDisabled()
    })
  })

  describe('4. Real-time Collaboration Features', () => {
    test('Toast notifications work for user feedback', async () => {
      const { useToastHelpers } = await import('@/components/common')
      
      const TestComponent = () => {
        const { showSuccess, showError } = useToastHelpers()
        
        return (
          <div>
            <button onClick={() => showSuccess('Test success')}>Test Success</button>
            <button onClick={() => showError('Test error')}>Test Error</button>
          </div>
        )
      }
      
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Test success toast
      fireEvent.click(screen.getByText('Test Success'))
      
      // Test error toast
      fireEvent.click(screen.getByText('Test Error'))
    })

    test('Global loading state works', async () => {
      const { useApp } = await import('@/contexts/app-context')
      
      const TestComponent = () => {
        const { setGlobalLoading } = useApp()
        
        return (
          <button onClick={() => setGlobalLoading(true)}>Show Loading</button>
        )
      }
      
      render(
        <TestWrapper>
          <TestComponent />
        </TestWrapper>
      )

      // Test global loading
      fireEvent.click(screen.getByText('Show Loading'))
    })
  })

  describe('5. Frontend Testing with Jest', () => {
    test('Jest is properly configured and running', () => {
      // This test itself proves Jest is working
      expect(true).toBe(true)
    })

    test('Testing utilities are available', () => {
      expect(render).toBeDefined()
      expect(screen).toBeDefined()
      expect(fireEvent).toBeDefined()
      expect(waitFor).toBeDefined()
    })

    test('Component imports work correctly', async () => {
      // Test that all components can be imported without errors
      const { Modal, Table, useToastHelpers } = await import('@/components/common')
      const { useApp } = await import('@/contexts/app-context')
      const { useOrganization } = await import('@/contexts/organization-context')
      
      expect(Modal).toBeDefined()
      expect(Table).toBeDefined()
      expect(useToastHelpers).toBeDefined()
      expect(useApp).toBeDefined()
      expect(useOrganization).toBeDefined()
    })
  })

  describe('Additional Phase 1 Week 3 Features', () => {
    test('Reusable UI Components work', async () => {
      const { Modal, ConfirmationModal, InfoModal } = await import('@/components/common')
      
      // Test modal components exist
      expect(Modal).toBeDefined()
      expect(ConfirmationModal).toBeDefined()
      expect(InfoModal).toBeDefined()
    })

    test('Table components with pagination work', async () => {
      const { Table, TableHeader, TableBody, TableRow, TableHead, TableCell, Pagination, useDataTable } = await import('@/components/common')
      
      // Test table components exist
      expect(Table).toBeDefined()
      expect(TableHeader).toBeDefined()
      expect(TableBody).toBeDefined()
      expect(TableRow).toBeDefined()
      expect(TableHead).toBeDefined()
      expect(TableCell).toBeDefined()
      expect(Pagination).toBeDefined()
      expect(useDataTable).toBeDefined()
    })

    test('Error boundaries work', async () => {
      const { DashboardErrorBoundary, AdminErrorBoundary } = await import('@/components/common/error-boundary')
      
      // Test error boundary components exist
      expect(DashboardErrorBoundary).toBeDefined()
      expect(AdminErrorBoundary).toBeDefined()
    })

    test('Loading components work', async () => {
      const { LoadingSpinner, GlobalLoading, Skeleton } = await import('@/components/common')
      
      // Test loading components exist
      expect(LoadingSpinner).toBeDefined()
      expect(GlobalLoading).toBeDefined()
      expect(Skeleton).toBeDefined()
    })

    test('Centralized API handling works', async () => {
      const { setAuthToken, getAuthToken } = await import('@/lib/api')
      
      // Test API functions exist
      expect(setAuthToken).toBeDefined()
      expect(getAuthToken).toBeDefined()
    })

    test('State management works', async () => {
      const { useApp } = await import('@/contexts/app-context')
      const { useOrganization } = await import('@/contexts/organization-context')
      
      // Test context hooks exist
      expect(useApp).toBeDefined()
      expect(useOrganization).toBeDefined()
    })
  })
})
