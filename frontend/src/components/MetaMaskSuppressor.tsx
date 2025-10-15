"use client"

import { useEffect } from 'react'

/**
 * MetaMask Suppressor Component
 * Prevents MetaMask extension from auto-connecting and suppresses related errors
 */
export function MetaMaskSuppressor() {
  useEffect(() => {
    if (typeof window === 'undefined') return

    // Suppress MetaMask auto-connection attempts
    const suppressMetaMask = () => {
      // Override window.ethereum to prevent auto-connection
      if (window.ethereum) {
        const originalEthereum = window.ethereum
        
        // Create a mock ethereum object that doesn't auto-connect
        const mockEthereum = {
          ...originalEthereum,
          request: async (args: any) => {
            // Suppress connection requests
            if (args.method === 'eth_requestAccounts' || args.method === 'eth_accounts') {
              throw new Error('MetaMask connection disabled for this application')
            }
            return originalEthereum.request(args)
          },
          isConnected: () => false,
          isMetaMask: false
        }
        
        // Replace the ethereum object
        Object.defineProperty(window, 'ethereum', {
          value: mockEthereum,
          writable: false,
          configurable: false
        })
      }

      // Override web3 if it exists
      if (window.web3) {
        Object.defineProperty(window, 'web3', {
          value: undefined,
          writable: false,
          configurable: false
        })
      }
    }

    // Apply suppression immediately
    suppressMetaMask()

    // Re-apply suppression periodically in case MetaMask tries to re-inject
    const interval = setInterval(suppressMetaMask, 1000)

    // Cleanup
    return () => {
      clearInterval(interval)
    }
  }, [])

  return null // This component doesn't render anything
}

export default MetaMaskSuppressor





