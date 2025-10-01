"use client"

import { UserButton } from '@clerk/nextjs'

export function AuthUserButton() {
  return <UserButton afterSignOutUrl="/" />
}

