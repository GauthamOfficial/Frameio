/**
 * MetaMask Suppression Utilities
 * Comprehensive solution to prevent MetaMask auto-connection and suppress related errors
 */

// Check if an error is MetaMask-related
export const isMetaMaskError = (error: unknown): boolean => {
    const errorObj = error as { toString?: () => string; message?: string; stack?: string }
  if (!error) return false
  
  const errorString = errorObj.toString?.()?.toLowerCase() || ''
  const message = errorObj.message?.toLowerCase() || ''
  const stack = errorObj.stack?.toLowerCase() || ''
  
  return (
    errorString.includes('metamask') ||
    errorString.includes('failed to connect') ||
    errorString.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    errorString.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    errorString.includes('at object.connect') ||
    message.includes('metamask') ||
    message.includes('failed to connect') ||
    message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    message.includes('at object.connect') ||
    stack.includes('metamask') ||
    stack.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    stack.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
    stack.includes('at object.connect')
  )
}

// Suppress MetaMask errors in console
export const suppressMetaMaskConsoleErrors = () => {
  if (typeof window === 'undefined') return

  const originalConsoleError = console.error
  const originalConsoleWarn = console.warn
  const originalConsoleLog = console.log
  
  console.error = (...args: unknown[]) => {
    const message = args.join(' ').toLowerCase()
    
    if (
      message.includes('metamask') ||
      message.includes('failed to connect') ||
      message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('at object.connect')
    ) {
      // Suppress MetaMask errors
      return
    }
    
    originalConsoleError.apply(console, args)
  }
  
  console.warn = (...args: unknown[]) => {
    const message = args.join(' ').toLowerCase()
    
    if (
      message.includes('metamask') ||
      message.includes('failed to connect') ||
      message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('at object.connect')
    ) {
      // Suppress MetaMask warnings
      return
    }
    
    originalConsoleWarn.apply(console, args)
  }
  
  // Also suppress console.log for MetaMask messages
  console.log = (...args: unknown[]) => {
    const message = args.join(' ').toLowerCase()
    
    if (
      message.includes('metamask') ||
      message.includes('failed to connect') ||
      message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn')
    ) {
      // Suppress MetaMask logs
      return
    }
    
    originalConsoleLog.apply(console, args)
  }
}

// Handle unhandled promise rejections
export const suppressMetaMaskPromiseRejections = () => {
  if (typeof window === 'undefined') return

  window.addEventListener('unhandledrejection', (event) => {
    if (isMetaMaskError(event.reason)) {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
  }, true) // Use capture phase
}

// Handle general errors
export const suppressMetaMaskErrors = () => {
  if (typeof window === 'undefined') return

  window.addEventListener('error', (event) => {
    const errorString = (event.error?.toString() || '').toLowerCase()
    const filename = (event.filename || '').toLowerCase()
    
    if (
      isMetaMaskError(event.error) || 
      isMetaMaskError(event.message) ||
      errorString.includes('at object.connect') ||
      filename.includes('nkbihfbeogaeaoehlefnkodbefgpgknn')
    ) {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
  }, true) // Use capture phase
}

// Initialize all MetaMask suppression
export const initializeMetaMaskSuppression = () => {
  if (typeof window === 'undefined') return

  suppressMetaMaskConsoleErrors()
  suppressMetaMaskPromiseRejections()
  suppressMetaMaskErrors()
  
  // Override any attempts to access MetaMask
  const originalDefineProperty = Object.defineProperty
  Object.defineProperty = function<T>(obj: T, prop: PropertyKey, descriptor: PropertyDescriptor & ThisType<T>): T {
    if (prop === 'ethereum' && descriptor.value && typeof descriptor.value === 'object' && descriptor.value !== null && 'isMetaMask' in descriptor.value && (descriptor.value as { isMetaMask?: unknown }).isMetaMask) {
      // Prevent MetaMask from being set as ethereum provider
      return obj
    }
    return originalDefineProperty.call(this, obj, prop, descriptor) as T
  }
}

// Auto-initialize if in browser
if (typeof window !== 'undefined') {
  initializeMetaMaskSuppression()
}





