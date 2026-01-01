'use client';

import * as React from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

interface DialogContentProps {
  children: React.ReactNode;
  className?: string;
}

interface DialogHeaderProps {
  children: React.ReactNode;
  className?: string;
}

interface DialogTitleProps {
  children: React.ReactNode;
  className?: string;
}

interface DialogDescriptionProps {
  children: React.ReactNode;
  className?: string;
}

interface DialogFooterProps {
  children: React.ReactNode;
  className?: string;
}

export function Dialog({ open, onOpenChange, children }: DialogProps) {
  React.useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && open) {
        onOpenChange(false);
      }
    };

    if (open) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [open, onOpenChange]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        onClick={() => onOpenChange(false)}
      />
      <div className="relative z-50 w-full max-w-full">{children}</div>
    </div>
  );
}

export function DialogContent({ children, className = '' }: DialogContentProps) {
  return (
    <div
      className={`bg-card text-card-foreground rounded-lg shadow-lg p-4 sm:p-6 max-w-md w-full mx-auto border border-border ${className}`}
    >
      {children}
    </div>
  );
}

export function DialogHeader({ children, className = '' }: DialogHeaderProps) {
  return <div className={`mb-4 ${className}`}>{children}</div>;
}

export function DialogTitle({ children, className = '' }: DialogTitleProps) {
  return <h2 className={`text-lg font-semibold text-foreground ${className}`}>{children}</h2>;
}

export function DialogDescription({ children, className = '' }: DialogDescriptionProps) {
  return <p className={`text-sm text-muted-foreground mt-1 ${className}`}>{children}</p>;
}

export function DialogFooter({ children, className = '' }: DialogFooterProps) {
  return <div className={`flex justify-end gap-2 mt-6 ${className}`}>{children}</div>;
}

export function DialogClose({ onClose }: { onClose: () => void }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="absolute right-4 top-4"
      onClick={onClose}
    >
      <X className="h-4 w-4" />
    </Button>
  );
}






