"use client"

import React from 'react'
import { useAppContext } from '@/contexts/app-context'

export function TestContext() {
  try {
    const context = useAppContext()
    console.log('App context loaded successfully:', context)
    return (
      <div className="p-4 bg-green-100 border border-green-400 rounded">
        <h3 className="text-green-800 font-bold">✅ App Context Working</h3>
        <p className="text-green-700">Token: {context?.token ? 'Present' : 'Not present'}</p>
        <p className="text-green-700">Authenticated: {context?.isAuthenticated ? 'Yes' : 'No'}</p>
      </div>
    )
  } catch (error) {
    console.error('App context error:', error)
    return (
      <div className="p-4 bg-red-100 border border-red-400 rounded">
        <h3 className="text-red-800 font-bold">❌ App Context Error</h3>
        <p className="text-red-700">Error: {error instanceof Error ? error.message : 'Unknown error'}</p>
      </div>
    )
  }
}
