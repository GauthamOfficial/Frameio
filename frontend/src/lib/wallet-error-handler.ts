// Handle MetaMask and wallet connection errors gracefully
export const handleWalletErrors = () => {
  if (typeof window === 'undefined') return

  // Handle unhandled promise rejections from wallet connections
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason
    const errorString = error ? (error.toString() + (error.message || '') + (error.stack || '')).toLowerCase() : ''
    
    // Check if it's a MetaMask or wallet-related error
    if (
      error?.message?.includes('MetaMask') ||
      error?.message?.includes('Failed to connect') ||
      error?.message?.includes('extension not found') ||
      error?.message?.includes('wallet') ||
      error?.message?.includes('ethereum') ||
      error?.message?.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      error?.stack?.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      errorString.includes('at object.connect') ||
      errorString.includes('metamask')
    ) {
      // Suppress the error since we don't use wallets in this app
      event.preventDefault() // Prevent the error from being logged
      event.stopPropagation()
      return false
    }
  }, true) // Use capture phase

  // Handle console errors from injected scripts
  const originalConsoleError = console.error
  console.error = (...args) => {
    const message = args.join(' ').toLowerCase()
    
    // Suppress MetaMask/wallet related errors
    if (
      message.includes('metamask') ||
      message.includes('failed to connect') ||
      message.includes('extension not found') ||
      message.includes('wallet') ||
      message.includes('ethereum') ||
      message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('at object.connect')
    ) {
      return // Suppress completely
    }
    
    // Call original console.error for other errors
    originalConsoleError.apply(console, args)
  }

  // Handle specific MetaMask extension errors
  window.addEventListener('error', (event) => {
    const error = event.error
    const message = (event.message || '').toLowerCase()
    const filename = (event.filename || '').toLowerCase()
    const errorString = error ? (error.toString() + (error.message || '') + (error.stack || '')).toLowerCase() : ''
    
    if (
      message.includes('metamask') ||
      message.includes('failed to connect') ||
      message.includes('chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      message.includes('at object.connect') ||
      filename.includes('nkbihfbeogaeaoehlefnkodbefgpgknn') ||
      (error && errorString.includes('metamask')) ||
      (error && errorString.includes('at object.connect'))
    ) {
      event.preventDefault()
      event.stopPropagation()
      return false
    }
  }, true) // Use capture phase
}

// Initialize error handling
if (typeof window !== 'undefined') {
  handleWalletErrors()
}
