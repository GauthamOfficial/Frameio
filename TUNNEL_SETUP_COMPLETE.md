# Tunnel Setup - Complete Fix

## Problem Fixed ✅

When accessing via Cloudflare Tunnel:
- ❌ Poster generation failed (couldn't reach backend)
- ❌ Generated posts didn't show (couldn't fetch from backend)

## Solution Applied ✅

Updated the code to:
1. **Detect tunnel access** - Check if URL contains `trycloudflare.com` or `ngrok.io`
2. **Use relative paths** - When accessed via tunnel, use `/api/...` paths
3. **Next.js rewrites proxy** - Next.js automatically proxies `/api/*` to `http://localhost:8000/api/*`

## What Changed

### 1. Poster Generator (`enhanced-poster-generator-with-branding.tsx`)
- Now detects tunnel access
- Uses relative paths first when accessed via tunnel
- Next.js rewrites proxy to localhost backend

### 2. Social Media Page (`social-media/page.tsx`)
- Now detects tunnel access
- Uses relative paths when accessed via tunnel
- Can fetch generated posts via tunnel

## How It Works

1. **You access:** `https://resolution-cornell-bedding-equations.trycloudflare.com/dashboard/poster-generator`
2. **Component detects:** "This is a tunnel URL"
3. **Makes request to:** `/api/ai/ai-poster/generate_poster/` (relative path)
4. **Next.js rewrites:** Proxies to `http://localhost:8000/api/ai/ai-poster/generate_poster/`
5. **Backend responds:** Through Next.js proxy back to frontend
6. **Works!** ✅

## Setup Required

### Step 1: Ensure Backend is Running
```bash
cd backend
python manage.py runserver
```

### Step 2: Start Frontend Tunnel
```bash
node start-cloudflare-tunnel.js
```

### Step 3: Set Environment Variable
In `frontend/.env.local`:
```bash
NEXT_PUBLIC_APP_URL=https://your-tunnel-url.trycloudflare.com
```

### Step 4: Restart Frontend
```bash
cd frontend
npm run dev
```

## Testing

1. **Access via tunnel:** `https://your-tunnel-url.trycloudflare.com/dashboard/poster-generator`
2. **Generate a poster** - Should work now! ✅
3. **Check social media page:** `https://your-tunnel-url.trycloudflare.com/dashboard/social-media`
4. **See generated posts** - Should show now! ✅

## Important Notes

- ✅ **Only ONE tunnel needed** - For frontend (port 3000)
- ✅ **Backend stays on localhost:8000** - Next.js rewrites proxy it
- ✅ **Works for both localhost and tunnel** - Code detects which one
- ✅ **No backend tunnel needed** - Next.js handles the proxy

## Troubleshooting

### Still getting errors?

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health/
   ```

2. **Check Next.js rewrites:**
   - Verify `next.config.ts` has rewrites configured
   - Restart frontend after any config changes

3. **Check browser console:**
   - Look for "Tunnel access detected" messages
   - Check for network errors

4. **Verify tunnel is running:**
   - Visit tunnel URL in browser
   - Should see your frontend

## Summary

✅ **Fixed:** Poster generation via tunnel
✅ **Fixed:** Fetching generated posts via tunnel  
✅ **No changes needed:** Backend stays on localhost
✅ **One tunnel:** Only need frontend tunnel

Everything should work now! 🎉




