// Handle chunk loading errors gracefully
export const handleChunkErrors = () => {
  if (typeof window === 'undefined') return

  // Handle chunk loading errors
  window.addEventListener('error', (event) => {
    const error = event.error
    
    // Check if it's a chunk loading error
    if (
      error?.name === 'ChunkLoadError' ||
      error?.message?.includes('Loading chunk') ||
      error?.message?.includes('failed') ||
      false // Additional error checks can be added here
    ) {
      console.warn('Chunk loading error detected, attempting recovery:', error?.message || 'Unknown chunk error')
      
      // Attempt to reload the page after a short delay
      setTimeout(() => {
        console.log('Reloading page to recover from chunk loading error...')
        window.location.reload()
      }, 1000)
      
      // Prevent the error from propagating
      event.preventDefault()
      return false
    }
  })

  // Handle unhandled promise rejections from chunk loading
  window.addEventListener('unhandledrejection', (event) => {
    const error = event.reason
    
    // Check if it's a chunk loading related error
    if (
      error?.message?.includes('Loading chunk') ||
      error?.message?.includes('ChunkLoadError') ||
      false // Additional error checks can be added here
    ) {
      console.warn('Chunk loading promise rejection detected:', error.message)
      
      // Attempt to reload the page
      setTimeout(() => {
        console.log('Reloading page to recover from chunk loading promise rejection...')
        window.location.reload()
      }, 1000)
      
      // Prevent the error from being logged
      event.preventDefault()
    }
  })

  // Add a global error handler for network errors
  const originalFetch = window.fetch
  window.fetch = async (...args) => {
    try {
      return await originalFetch(...args)
    } catch (error: unknown) {
      // Type guard to check if error is an Error instance
      const isError = (e: unknown): e is Error => {
        return e instanceof Error || (typeof e === 'object' && e !== null && 'message' in e && typeof (e as { message: unknown }).message === 'string')
      }
      
      const errorMessage = isError(error) ? error.message : ''
      
      // Check if it's a chunk loading error
      if (
        errorMessage.includes('Loading chunk') ||
        errorMessage.includes('ChunkLoadError') ||
        false // Additional error checks can be added here
      ) {
        console.warn('Fetch error for chunk, attempting recovery:', errorMessage)
        
        // Retry the fetch after a short delay
        await new Promise(resolve => setTimeout(resolve, 1000))
        return await originalFetch(...args)
      }
      throw error
    }
  }
}

// Initialize chunk error handling
if (typeof window !== 'undefined') {
  handleChunkErrors()
}
