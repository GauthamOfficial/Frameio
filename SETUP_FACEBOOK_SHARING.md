# Setup Facebook Sharing - Step by Step

## Problem
You're seeing: "Facebook sharing requires a public URL. Please set up Cloudflare Tunnel or ngrok."

This happens because Facebook cannot access `localhost` URLs. You need a public URL.

## Solution: Use Cloudflare Tunnel (Free, No Account Required)

### Step 1: Start Cloudflare Tunnel

Open a **new terminal/PowerShell window** and run:

```bash
cd "D:\My Files\Yarl IT Hub\Framio"
node start-cloudflare-tunnel.js
```

**What you'll see:**
```
🔍 Checking Cloudflare Tunnel installation...
✅ Cloudflare Tunnel is installed
🚀 Starting Cloudflare Tunnel...

+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
|  https://abc123-def456-ghi789.trycloudflare.com                                           |
+--------------------------------------------------------------------------------------------+
```

**IMPORTANT:** Copy the URL shown (e.g., `https://abc123-def456-ghi789.trycloudflare.com`)

**Keep this terminal window open!** The tunnel must stay running.

### Step 2: Create/Update Environment File

1. **Navigate to frontend folder:**
   ```bash
   cd frontend
   ```

2. **Create or edit `.env.local` file:**
   ```bash
   # If file doesn't exist, create it
   # If it exists, open it in your editor
   ```

3. **Add this line** (replace with YOUR tunnel URL):
   ```bash
   NEXT_PUBLIC_APP_URL=https://abc123-def456-ghi789.trycloudflare.com
   ```

   **Example:**
   ```bash
   NEXT_PUBLIC_APP_URL=https://abc123-def456-ghi789.trycloudflare.com
   ```

### Step 3: Restart Frontend Server

1. **Stop your frontend** (if running):
   - Press `Ctrl+C` in the terminal where frontend is running

2. **Start frontend again:**
   ```bash
   npm run dev
   ```

### Step 4: Test Facebook Sharing

1. **Go to:** `http://localhost:3000/dashboard/social-media`
2. **Click "Share on Facebook"** on any poster
3. **Facebook should now open with preview!** ✅

## Complete Setup Checklist

- [ ] Cloudflare Tunnel is running (terminal window open)
- [ ] Copied the tunnel URL from tunnel output
- [ ] Created/updated `frontend/.env.local` with `NEXT_PUBLIC_APP_URL`
- [ ] Restart frontend server
- [ ] Test Facebook sharing - should work now!

## Troubleshooting

### Issue: "Tunnel URL not found"

**Fix:** Make sure the tunnel terminal is still running. If it closed, restart it:
```bash
node start-cloudflare-tunnel.js
```

### Issue: "Still getting localhost error"

**Fix:** 
1. Check `frontend/.env.local` exists and has the correct URL
2. Make sure you restarted the frontend after adding the env variable
3. Check the URL doesn't have trailing slash: `https://abc123.trycloudflare.com` (not `https://abc123.trycloudflare.com/`)

### Issue: "Tunnel URL changes every time"

**This is normal!** Cloudflare Tunnel generates new URLs each time.

**Fix:** 
1. Update `NEXT_PUBLIC_APP_URL` in `frontend/.env.local` after each restart
2. Restart frontend after updating

### Issue: "Facebook still shows no image"

**Fix:**
1. Test the poster URL in Facebook Sharing Debugger:
   - Visit: https://developers.facebook.com/tools/debug/
   - Paste: `https://your-tunnel-url/poster/{poster-id}`
   - Click "Debug"
   - Click "Scrape Again" to refresh

2. Verify image URL is accessible:
   - Visit the image URL directly in browser
   - Should show the image, not 404

## Quick Reference

**Start Tunnel:**
```bash
node start-cloudflare-tunnel.js
```

**Set Environment Variable:**
```bash
# In frontend/.env.local
NEXT_PUBLIC_APP_URL=https://your-tunnel-url-here
```

**Restart Frontend:**
```bash
# Stop (Ctrl+C), then:
npm run dev
```

## Alternative: Use ngrok (If You Have Account)

If you prefer ngrok:

1. **Sign up:** https://dashboard.ngrok.com/signup
2. **Get authtoken:** https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure:**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN
   ```
4. **Start:**
   ```bash
   ngrok http 3000
   ```
5. **Set environment variable:**
   ```bash
   NEXT_PUBLIC_APP_URL=https://your-ngrok-url.ngrok.io
   ```

## Need Help?

- Check `FACEBOOK_SHARING_TROUBLESHOOTING.md` for more details
- Verify tunnel is accessible: Visit tunnel URL in browser
- Check frontend console for errors
- Verify backend is running on port 8000




