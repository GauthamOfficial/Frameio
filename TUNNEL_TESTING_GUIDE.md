# Tunnel Testing Guide - Browser Automation

## Issue: Tunnel Not Running

The tunnel at `https://resolution-cornell-bedding-equations.trycloudflare.com` is showing **Error 1033** - Cloudflare Tunnel is not reachable.

## Quick Fix

### Step 1: Start the Tunnel

```bash
node start-cloudflare-tunnel.js
```

**Wait for the tunnel URL to appear.** It will look like:
```
✓ Cloudflare Tunnel is running
Public URL: https://some-random-words.trycloudflare.com
```

### Step 2: Update Environment Variable

Copy the new tunnel URL and update `frontend/.env.local`:

```bash
NEXT_PUBLIC_APP_URL=https://your-new-tunnel-url.trycloudflare.com
```

### Step 3: Restart Frontend (if needed)

```bash
cd frontend
npm run dev
```

### Step 4: Test in Browser

Visit the new tunnel URL:
```
https://your-new-tunnel-url.trycloudflare.com/dashboard
```

---

## Automated Testing with Playwright

I can create two types of tests for you:

### 1. Manual Testing (What I Can Do Now)

Once your tunnel is running, I can:
- ✅ Navigate to your tunnel URL
- ✅ Check if dashboard loads without errors
- ✅ Test poster generation
- ✅ Verify Facebook share dialog
- ✅ Check network requests in browser console
- ✅ Take screenshots for verification

### 2. Playwright Test Suite (Code I Can Create)

I can create test files you can run anytime:

```
tests/
├── tunnel-dashboard.spec.ts    # Test dashboard loads
├── poster-generator.spec.ts    # Test poster generation
├── facebook-share.spec.ts      # Test Facebook sharing
└── api-integration.spec.ts     # Test API calls via tunnel
```

---

## What Would You Like?

### Option A: Test Now (Recommended)
1. Start your tunnel with `node start-cloudflare-tunnel.js`
2. Tell me the new tunnel URL
3. I'll test it with browser automation and report any issues

### Option B: Create Playwright Tests
I'll create test files you can run with:
```bash
npm run test:e2e
```

### Option C: Both
Do option A first to verify everything works, then create the test suite.

---

## Current Status

❌ **Tunnel not running**
- Error: Cloudflare Tunnel error (1033)
- Cause: `cloudflared` process stopped or frontend not running
- Fix: Run `node start-cloudflare-tunnel.js`

⏳ **Waiting for:**
- Tunnel to start
- New tunnel URL

---

## Next Steps

1. **Start tunnel:**
   ```bash
   node start-cloudflare-tunnel.js
   ```

2. **Copy the tunnel URL** that appears (it might be different from before)

3. **Tell me the new URL** so I can test it

4. **Or provide the URL and I'll:**
   - Navigate to your app
   - Check for errors
   - Test poster generation
   - Verify Facebook sharing
   - Report results

---

## Why Did the Tunnel Stop?

Cloudflare Tunnel URLs can change when:
- ✗ The process was stopped (Ctrl+C)
- ✗ Computer went to sleep
- ✗ Terminal was closed
- ✗ Network connection dropped

**Solution:** Keep the tunnel running in a dedicated terminal window while testing.

---

## Reminder: Tunnel Architecture

```
Browser → Cloudflare Tunnel (port 3000) → Next.js → Rewrites → Django (port 8000)
          ↑
          Must be running!
```

Both need to be running:
1. ✅ Backend: `python manage.py runserver` (port 8000)
2. ✅ Frontend: `npm run dev` (port 3000)
3. ✅ Tunnel: `node start-cloudflare-tunnel.js` (exposes port 3000)




