# Fix: Backend Not Accessible via Tunnel

## Problem

When accessing the app via Cloudflare Tunnel (`https://resolution-cornell-bedding-equations.trycloudflare.com`):
- ✅ Frontend loads
- ❌ Poster generation fails (can't reach backend)
- ❌ Generated posts don't show (can't fetch from backend)

**Root Cause:** The tunnel only exposes port 3000 (frontend), but the backend runs on port 8000 which isn't accessible through the tunnel.

## Solution: Run Second Tunnel for Backend

### Step 1: Start Backend Tunnel

Open a **second terminal/PowerShell window** and run:

```bash
cd "D:\My Files\Yarl IT Hub\Framio"
node start-cloudflare-tunnel.js
```

**Wait!** This will conflict with your frontend tunnel. Instead, run manually:

```bash
# In a NEW terminal window
cloudflared tunnel --url http://localhost:8000
```

You'll get a **different URL** for the backend, like:
```
https://backend-xyz123.trycloudflare.com
```

### Step 2: Update Environment Variables

Update `frontend/.env.local`:

```bash
# Frontend tunnel URL (for Facebook sharing)
NEXT_PUBLIC_APP_URL=https://resolution-cornell-bedding-equations.trycloudflare.com

# Backend tunnel URL (for API calls)
NEXT_PUBLIC_API_BASE_URL=https://backend-xyz123.trycloudflare.com
NEXT_PUBLIC_API_URL=https://backend-xyz123.trycloudflare.com/api
```

### Step 3: Restart Frontend

```bash
# Stop frontend (Ctrl+C)
# Then restart
npm run dev
```

## Alternative Solution: Use Next.js API Rewrites (Recommended)

This is better because you only need ONE tunnel!

### Step 1: Update `frontend/next.config.ts`

Add rewrites to proxy API calls:

```typescript
async rewrites() {
  return [
    {
      source: '/api/:path*',
      destination: 'http://localhost:8000/api/:path*',
    },
  ]
}
```

### Step 2: Update Components to Use Relative Paths

The poster generator already uses relative paths (`/api/ai/...`), so this should work!

### Step 3: Restart Frontend

```bash
npm run dev
```

## Quick Fix: Update Environment Variables

If you want to keep using absolute URLs, you need BOTH tunnels:

1. **Frontend tunnel:** `https://resolution-cornell-bedding-equations.trycloudflare.com`
2. **Backend tunnel:** Run `cloudflared tunnel --url http://localhost:8000` in a new terminal

Then update `frontend/.env.local`:
```bash
NEXT_PUBLIC_APP_URL=https://resolution-cornell-bedding-equations.trycloudflare.com
NEXT_PUBLIC_API_BASE_URL=https://your-backend-tunnel-url.trycloudflare.com
NEXT_PUBLIC_API_URL=https://your-backend-tunnel-url.trycloudflare.com/api
```

## Recommended: Use Next.js Rewrites (Easier)

This way you only need ONE tunnel for the frontend, and Next.js will proxy API calls to localhost backend.




