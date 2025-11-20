# How to Get Your Facebook Share URL

## Step-by-Step Guide

### Step 1: Get Your Tunnel URL

1. **Start Cloudflare Tunnel:**
   ```bash
   node start-cloudflare-tunnel.js
   ```

2. **Look for the output** - it will show something like:
   ```
   +--------------------------------------------------------------------------------------------+
   |  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable): |
   |  https://abc123-def456-ghi789.trycloudflare.com                                           |
   +--------------------------------------------------------------------------------------------+
   ```

3. **Copy the URL** (e.g., `https://abc123-def456-ghi789.trycloudflare.com`)

### Step 2: Get Your Poster ID

1. **Go to your social media page:**
   ```
   http://localhost:3000/dashboard/social-media
   ```

2. **Find a poster** you want to share

3. **Get the poster ID** - it's a UUID that looks like:
   ```
   a1b2c3d4-e5f6-7890-abcd-ef1234567890
   ```
   
   You can find it by:
   - Looking at the poster data in browser DevTools
   - Or clicking "View" on a poster and checking the URL

### Step 3: Build Your Share URL

Combine them like this:
```
https://your-tunnel-url/poster/your-poster-id
```

**Example:**
```
https://abc123-def456-ghi789.trycloudflare.com/poster/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### Step 4: Test in Facebook Sharing Debugger

1. **Visit:** https://developers.facebook.com/tools/debug/
2. **Paste your actual URL** (not the placeholder!)
3. **Click "Debug"**

## Quick Method: Get URL from Browser

1. **Start your tunnel** and set `NEXT_PUBLIC_APP_URL`
2. **Go to:** `http://localhost:3000/dashboard/social-media`
3. **Click "View"** on a poster (or right-click → Copy link)
4. **The URL in your browser** will be the correct share URL!

## Still Getting "Malformed URL" Error?

Make sure:
- ✅ URL starts with `https://` (not `http://localhost`)
- ✅ URL doesn't contain `{poster-id}` or `your-tunnel-url` (use actual values)
- ✅ Poster ID is a valid UUID (not placeholder text)
- ✅ Tunnel is running and accessible

## Example of Correct vs Incorrect URLs

❌ **WRONG:**
```
https://your-tunnel-url/poster/{poster-id}
http://localhost:3000/poster/abc123
```

✅ **CORRECT:**
```
https://abc123-def456-ghi789.trycloudflare.com/poster/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```



