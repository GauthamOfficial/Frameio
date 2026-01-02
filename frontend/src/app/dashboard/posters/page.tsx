"use client"

import { SavedPosters } from "@/components/dashboard/saved-posters"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Image } from "lucide-react"

export default function PostersPage() {
  return (
    <div className="container mx-auto p-4 sm:p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {/* eslint-disable-next-line jsx-a11y/alt-text */}
            <Image className="h-5 w-5" aria-hidden="true" />
            All Generated Posters
          </CardTitle>
        </CardHeader>
        <CardContent>
          <SavedPosters />
        </CardContent>
      </Card>
    </div>
  )
}

