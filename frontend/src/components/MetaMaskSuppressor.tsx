"use client"

import { useEffect, useRef } from 'react'

// Extend Window interface to include ethereum property
declare global {
  interface Window {
    ethereum?: {
      isMetaMask?: boolean
      request?: (args: { method: string; params?: unknown[] }) => Promise<unknown>
      isConnected?: () => boolean
      [key: string]: unknown
    }
    web3?: unknown
  }
}

/**
 * MetaMask Suppressor Component
 * Prevents MetaMask extension from auto-connecting and suppresses related errors
 */
export function MetaMaskSuppressor() {
  const suppressedRef = useRef(false)

  useEffect(() => {
    if (typeof window === 'undefined') return

    // Suppress MetaMask auto-connection attempts
    const suppressMetaMask = () => {
      // Skip if already suppressed to avoid unnecessary operations
      if (suppressedRef.current && window.ethereum && !window.ethereum.isMetaMask) {
        return
      }

      try {
        // Override window.ethereum to prevent auto-connection
        if (window.ethereum && !suppressedRef.current) {
          const originalEthereum = window.ethereum
          
          // Create a mock ethereum object that doesn't auto-connect
          const mockEthereum = {
            ...originalEthereum,
            // eslint-disable-next-line @typescript-eslint/no-explicit-any
            request: async (args: any) => {
              // Suppress connection requests
              if (args.method === 'eth_requestAccounts' || args.method === 'eth_accounts') {
                throw new Error('MetaMask connection disabled for this application')
              }
              return originalEthereum.request?.(args)
            },
            isConnected: () => false,
            isMetaMask: false
          }
          
          // Replace the ethereum object only if configurable
          try {
            Object.defineProperty(window, 'ethereum', {
              value: mockEthereum,
              writable: false,
              configurable: true // Changed to true to allow redefinition if needed
            })
            suppressedRef.current = true
          } catch (e) {
            // If property is not configurable, just suppress silently
            console.warn('Could not override window.ethereum:', e)
          }
        }

        // Override web3 if it exists
        if (window.web3) {
          try {
            Object.defineProperty(window, 'web3', {
              value: undefined,
              writable: false,
              configurable: true
            })
          } catch (e) {
            console.warn('Could not override window.web3:', e)
          }
        }
      } catch (error) {
        // Silently handle any errors to prevent page unresponsiveness
        console.warn('MetaMask suppression error:', error)
      }
    }

    // Apply suppression immediately
    suppressMetaMask()

    // Re-apply suppression less frequently (every 5 seconds instead of 1 second)
    // Only if MetaMask tries to re-inject
    const interval = setInterval(() => {
      if (window.ethereum?.isMetaMask) {
        suppressedRef.current = false
        suppressMetaMask()
      }
    }, 5000)

    // Cleanup
    return () => {
      clearInterval(interval)
    }
  }, [])

  return null // This component doesn't render anything
}

export default MetaMaskSuppressor





