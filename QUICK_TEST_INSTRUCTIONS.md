# Quick Test Instructions

## 🚀 Get Started in 3 Steps

### 1. Start Your Tunnel

```bash
node start-cloudflare-tunnel.js
```

**Wait for output like:**
```
✓ Cloudflare Tunnel is running
Public URL: https://abc-def-ghi.trycloudflare.com
```

### 2. Copy the Tunnel URL

The URL will look like: `https://some-random-words.trycloudflare.com`

### 3. Choose Your Testing Method

#### Option A: I'll Test It For You (Fastest)

Just reply with:
```
Test this URL: https://your-tunnel-url.trycloudflare.com
```

I'll use browser automation to:
- ✅ Navigate to your dashboard
- ✅ Check for errors
- ✅ Test poster generation
- ✅ Verify Facebook sharing
- ✅ Take screenshots
- ✅ Report results

#### Option B: Run Playwright Tests Yourself

```bash
cd frontend

# Install Playwright (first time only)
npm install -D @playwright/test
npx playwright install

# Run tests
TUNNEL_URL=https://your-tunnel-url.trycloudflare.com npm run test:e2e
```

**Windows PowerShell:**
```powershell
cd frontend
$env:TUNNEL_URL="https://your-tunnel-url.trycloudflare.com"
npm run test:e2e
```

---

## What I Created

### ✅ Playwright Test Suite

1. **`tests/tunnel-health.spec.ts`**
   - Checks tunnel works
   - Verifies no API errors
   - Confirms relative paths work

2. **`tests/poster-generation.spec.ts`**
   - Tests poster generator
   - Verifies API connections
   - Checks for console errors

3. **`tests/facebook-sharing.spec.ts`**
   - Tests Facebook sharing
   - Validates Open Graph tags
   - Checks public URL detection

4. **`playwright.config.ts`**
   - Configuration for all tests
   - Supports both localhost and tunnel
   - Generates HTML reports

### ✅ Code Fixes Applied

All dashboard components now:
- Detect tunnel access automatically
- Use relative paths via tunnel
- Fall back to absolute URLs on localhost

---

## Current Status

| Item | Status |
|------|--------|
| Code fixes | ✅ Done |
| Playwright tests created | ✅ Done |
| Tunnel running | ❌ Needs action |
| Ready to test | ⏳ Waiting for tunnel |

---

## What Happens When You Start the Tunnel

1. **You run:** `node start-cloudflare-tunnel.js`
2. **Tunnel starts:** Creates public URL
3. **You tell me:** Share the tunnel URL
4. **I test it:** Using browser automation
5. **You get results:** Pass/fail with screenshots

---

## Test Results You'll Get

### If Everything Works ✅

```
✓ Dashboard loads without errors
✓ Stats display correctly
✓ Posters list loads
✓ Branding kits load
✓ No ERR_BLOCKED_BY_CLIENT errors
✓ No CORS errors
✓ API calls use relative paths
✓ Poster generator loads
✓ Facebook sharing works
```

### If Issues Found ❌

You'll get:
- Specific error messages
- Screenshots of failures
- Console log errors
- Network request details
- Suggested fixes

---

## Ready?

**Start your tunnel and share the URL!**

```bash
node start-cloudflare-tunnel.js
```

Then tell me the URL and I'll run comprehensive tests via browser automation.




