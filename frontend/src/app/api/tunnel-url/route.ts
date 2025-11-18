import { NextRequest, NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET(request: NextRequest) {
  try {
    // Read the tunnel URL from the file
    const tunnelUrlPath = path.join(process.cwd(), 'tunnel-url.txt')
    
    if (fs.existsSync(tunnelUrlPath)) {
      const tunnelUrl = fs.readFileSync(tunnelUrlPath, 'utf8').trim()
      return new NextResponse(tunnelUrl, {
        status: 200,
        headers: {
          'Content-Type': 'text/plain',
          'Cache-Control': 'no-cache'
        }
      })
    } else {
      return new NextResponse('No tunnel URL found', {
        status: 404,
        headers: {
          'Content-Type': 'text/plain'
        }
      })
    }
  } catch (error) {
    console.error('Error reading tunnel URL:', error)
    return new NextResponse('Error reading tunnel URL', {
      status: 500,
      headers: {
        'Content-Type': 'text/plain'
      }
    })
  }
}








