"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { X } from "lucide-react"

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  className?: string
  size?: "sm" | "md" | "lg" | "xl"
  showCloseButton?: boolean
}

interface ModalHeaderProps {
  children: React.ReactNode
  className?: string
}

interface ModalContentProps {
  children: React.ReactNode
  className?: string
}

interface ModalFooterProps {
  children: React.ReactNode
  className?: string
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  className,
  size = "md",
  showCloseButton = true,
}) => {
  const sizeClasses = {
    sm: "max-w-md",
    md: "max-w-lg",
    lg: "max-w-2xl",
    xl: "max-w-4xl",
  }

  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener("keydown", handleEscape)
      document.body.style.overflow = "hidden"
    }

    return () => {
      document.removeEventListener("keydown", handleEscape)
      document.body.style.overflow = "unset"
    }
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      
      {/* Modal */}
      <div
        className={cn(
          "relative bg-background border rounded-lg shadow-lg w-full mx-4",
          sizeClasses[size],
          className
        )}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className="flex items-center justify-between p-6 border-b">
            {title && (
              <h2 className="text-lg font-semibold text-foreground">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <Button
                variant="ghost"
                size="icon"
                onClick={onClose}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        )}
        
        {/* Content */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  )
}

const ModalHeader: React.FC<ModalHeaderProps> = ({ children, className }) => (
  <div className={cn("mb-4", className)}>
    {children}
  </div>
)

const ModalContent: React.FC<ModalContentProps> = ({ children, className }) => (
  <div className={cn("mb-6", className)}>
    {children}
  </div>
)

const ModalFooter: React.FC<ModalFooterProps> = ({ children, className }) => (
  <div className={cn("flex justify-end space-x-2", className)}>
    {children}
  </div>
)

// Confirmation Modal Component
interface ConfirmationModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm: () => void
  title: string
  message: string
  confirmText?: string
  cancelText?: string
  variant?: "default" | "destructive"
  isLoading?: boolean
}

const ConfirmationModal: React.FC<ConfirmationModalProps> = ({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = "Confirm",
  cancelText = "Cancel",
  variant = "default",
  isLoading = false,
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <ModalContent>
        <p className="text-muted-foreground">{message}</p>
      </ModalContent>
      <ModalFooter>
        <Button variant="outline" onClick={onClose} disabled={isLoading}>
          {cancelText}
        </Button>
        <Button
          variant={variant}
          onClick={onConfirm}
          disabled={isLoading}
        >
          {isLoading ? "Loading..." : confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  )
}

// Info Modal Component
interface InfoModalProps {
  isOpen: boolean
  onClose: () => void
  title: string
  message: string
  buttonText?: string
}

const InfoModal: React.FC<InfoModalProps> = ({
  isOpen,
  onClose,
  title,
  message,
  buttonText = "OK",
}) => {
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={title} size="sm">
      <ModalContent>
        <p className="text-muted-foreground">{message}</p>
      </ModalContent>
      <ModalFooter>
        <Button onClick={onClose}>
          {buttonText}
        </Button>
      </ModalFooter>
    </Modal>
  )
}

export {
  Modal,
  ModalHeader,
  ModalContent,
  ModalFooter,
  ConfirmationModal,
  InfoModal,
}
