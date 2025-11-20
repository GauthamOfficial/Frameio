"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Modal, 
  ModalHeader, 
  ModalContent, 
  ModalFooter, 
  ConfirmationModal,
  InfoModal,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  Pagination,
  useDataTable,
  useToastHelpers,
  LoadingSpinner,
  Skeleton,
  SkeletonCard
} from "@/components/common"
import { useApp } from "@/contexts/app-context"
import { useOrganization } from "@/contexts/organization-context"
import { CheckCircle, XCircle, AlertCircle, Info } from "lucide-react"

export default function TestPhase1Week3Page() {
  const { isAuthenticated, user, userRole, permissions, isGlobalLoading, setGlobalLoading } = useApp()
  const { organizationId, userRole: orgUserRole, isLoading } = useOrganization()
  const { showSuccess, showError, showWarning, showInfo } = useToastHelpers()
  
  const [showModal, setShowModal] = useState(false)
  const [showConfirmModal, setShowConfirmModal] = useState(false)
  const [showInfoModal, setShowInfoModal] = useState(false)
  const [showLoading, setShowLoading] = useState(false)

  // Test data for table
  const testData = [
    { id: 1, name: "John Doe", email: "john@example.com", role: "Admin", status: "Active" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", role: "Designer", status: "Active" },
    { id: 3, name: "Bob Johnson", email: "bob@example.com", role: "Manager", status: "Inactive" },
  ]

  const {
    data: paginatedData,
    sort,
    currentPage,
    totalPages,
    handleSort,
    handlePageChange,
  } = useDataTable({
    data: testData,
    initialSort: { key: 'name', direction: 'asc' },
    initialPageSize: 2,
  })

  const testToast = (type: 'success' | 'error' | 'warning' | 'info') => {
    switch (type) {
      case 'success':
        showSuccess('Success!', 'This is a success message')
        break
      case 'error':
        showError('Error!', 'This is an error message')
        break
      case 'warning':
        showWarning('Warning!', 'This is a warning message')
        break
      case 'info':
        showInfo('Info!', 'This is an info message')
        break
    }
  }

  const testGlobalLoading = () => {
    setGlobalLoading(true)
    setTimeout(() => setGlobalLoading(false), 3000)
  }

  const testLocalLoading = () => {
    setShowLoading(true)
    setTimeout(() => setShowLoading(false), 2000)
  }

  const testConfirmAction = () => {
    showSuccess('Confirmed!', 'The action was confirmed')
    setShowConfirmModal(false)
  }

  return (
    <div className="space-y-8 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Phase 1 Week 3 - Test Page</h1>
          <p className="text-muted-foreground">Testing all implemented features</p>
        </div>
        <Badge variant="secondary">Test Mode</Badge>
      </div>

      {/* App State Display */}
      <Card>
        <CardHeader>
          <CardTitle>App State</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{isAuthenticated ? '✓' : '✗'}</div>
              <p className="text-sm text-muted-foreground">Authenticated</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{userRole || 'N/A'}</div>
              <p className="text-sm text-muted-foreground">User Role</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{organizationId ? '✓' : '✗'}</div>
              <p className="text-sm text-muted-foreground">Organization</p>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{permissions.length}</div>
              <p className="text-sm text-muted-foreground">Permissions</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Toast Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Toast Notifications</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => testToast('success')} variant="success">
              <CheckCircle className="mr-2 h-4 w-4" />
              Success Toast
            </Button>
            <Button onClick={() => testToast('error')} variant="destructive">
              <XCircle className="mr-2 h-4 w-4" />
              Error Toast
            </Button>
            <Button onClick={() => testToast('warning')} variant="warning">
              <AlertCircle className="mr-2 h-4 w-4" />
              Warning Toast
            </Button>
            <Button onClick={() => testToast('info')} variant="info">
              <Info className="mr-2 h-4 w-4" />
              Info Toast
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Modal Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Modal Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button onClick={() => setShowModal(true)}>
              Open Modal
            </Button>
            <Button onClick={() => setShowConfirmModal(true)} variant="destructive">
              Confirmation Modal
            </Button>
            <Button onClick={() => setShowInfoModal(true)} variant="info">
              Info Modal
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Loading States</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            <Button onClick={testGlobalLoading}>
              Test Global Loading
            </Button>
            <Button onClick={testLocalLoading} variant="outline">
              Test Local Loading
            </Button>
          </div>
          
          {showLoading && (
            <div className="mt-4">
              <LoadingSpinner size="md" text="Local loading test..." />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Skeleton Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Skeleton Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <SkeletonCard />
          </div>
        </CardContent>
      </Card>

      {/* Table Testing */}
      <Card>
        <CardHeader>
          <CardTitle>Data Table with Pagination</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>ID</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Email</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedData.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.id}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.email}</TableCell>
                  <TableCell>
                    <Badge variant={item.role === 'Admin' ? 'destructive' : 'secondary'}>
                      {item.role}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Badge variant={item.status === 'Active' ? 'default' : 'outline'}>
                      {item.status}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          
          {totalPages > 1 && (
            <div className="mt-4">
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modals */}
      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Test Modal">
        <ModalContent>
          <p>This is a test modal with custom content.</p>
        </ModalContent>
        <ModalFooter>
          <Button variant="outline" onClick={() => setShowModal(false)}>
            Cancel
          </Button>
          <Button onClick={() => setShowModal(false)}>
            Confirm
          </Button>
        </ModalFooter>
      </Modal>

      <ConfirmationModal
        isOpen={showConfirmModal}
        onClose={() => setShowConfirmModal(false)}
        onConfirm={testConfirmAction}
        title="Confirm Action"
        message="Are you sure you want to perform this action?"
        confirmText="Yes, do it"
        cancelText="Cancel"
        variant="destructive"
      />

      <InfoModal
        isOpen={showInfoModal}
        onClose={() => setShowInfoModal(false)}
        title="Information"
        message="This is an informational modal."
        buttonText="Got it"
      />
    </div>
  )
}
