"use client"

import React from 'react'
import TestTwoStepIntegration from '@/components/TestTwoStepIntegration'

export default function TestIntegrationPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Two-Step AI Integration Test
          </h1>
          <p className="text-muted-foreground">
            Test the complete Gemini 2.5 Flash + NanoBanana workflow
          </p>
        </div>
        
        <TestTwoStepIntegration />
      </div>
    </div>
  )
}
