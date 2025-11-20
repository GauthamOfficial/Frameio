# Facebook Sharing Troubleshooting

## Problem: Facebook Opens But Shows No Image or Caption

### Root Cause
Facebook **cannot access localhost URLs**. When you share `http://localhost:3000/poster/{id}`, Facebook's crawler tries to visit that URL but can't reach it because it's on your local machine.

### Solution: Use a Public Tunnel URL

You need to make your local server accessible to Facebook using a tunnel service.

## Quick Fix Steps

### Step 1: Start Cloudflare Tunnel

```bash
# In your project root
node start-cloudflare-tunnel.js
```

This will:
- Download Cloudflare Tunnel (if needed)
- Start a tunnel to `http://localhost:3000`
- Display a public URL like: `https://abc123.trycloudflare.com`

### Step 2: Set Environment Variable

Copy the public URL and add it to `frontend/.env.local`:

```bash
NEXT_PUBLIC_APP_URL=https://abc123.trycloudflare.com
```

### Step 3: Restart Frontend

```bash
# Stop your frontend (Ctrl+C)
# Then restart it
cd frontend
npm run dev
```

### Step 4: Test Again

1. Go to `http://localhost:3000/dashboard/social-media`
2. Click "Share on Facebook" on a poster
3. Facebook should now show the image and caption!

## Verify OG Tags

### Check Poster Page Source

1. Visit: `https://your-tunnel-url/poster/{poster-id}`
2. Right-click → View Page Source
3. Look for these tags in `<head>`:

```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="https://...">
<meta property="og:url" content="https://...">
```

### Test with Facebook Sharing Debugger

1. Visit: https://developers.facebook.com/tools/debug/
2. Paste your poster URL: `https://your-tunnel-url/poster/{poster-id}`
3. Click "Debug"
4. You should see:
   - ✅ Image preview
   - ✅ Title
   - ✅ Description
   - ✅ No errors

## Common Issues

### Issue: "Facebook sharing requires a public URL" Error

**Cause:** You're trying to share with localhost.

**Fix:** 
1. Start Cloudflare Tunnel: `node start-cloudflare-tunnel.js`
2. Set `NEXT_PUBLIC_APP_URL` in `frontend/.env.local`
3. Restart frontend

### Issue: Facebook Shows "No Image Available"

**Possible Causes:**
1. Image URL is not absolute (must start with `http://` or `https://`)
2. Image is not publicly accessible
3. Image URL returns 404 or error

**Fix:**
1. Check image URL in poster page source
2. Verify image loads when you visit the URL directly
3. Check backend share endpoint: `GET /api/ai/posters/{id}/share/`
4. Ensure image URL is absolute (not relative)

### Issue: Facebook Shows Wrong Title/Description

**Cause:** OG tags not being generated correctly.

**Fix:**
1. Check poster page source for OG tags
2. Verify share endpoint returns correct data
3. Clear Facebook's cache using Sharing Debugger ("Scrape Again")

### Issue: Tunnel URL Changes on Restart

**Cause:** Cloudflare Tunnel generates new URLs each time.

**Fix:**
1. Update `NEXT_PUBLIC_APP_URL` after each tunnel restart
2. Or use ngrok with a static domain (paid plan)

## Testing Checklist

- [ ] Cloudflare Tunnel is running
- [ ] `NEXT_PUBLIC_APP_URL` is set to tunnel URL
- [ ] Frontend is restarted after setting env variable
- [ ] Poster page loads at tunnel URL
- [ ] OG tags are present in page source
- [ ] Image URL is absolute and accessible
- [ ] Facebook Sharing Debugger shows preview correctly
- [ ] Share button opens Facebook with preview

## Quick Test Commands

```bash
# Test share endpoint
curl http://localhost:8000/api/ai/posters/{poster-id}/share/

# Test poster page
curl -I https://your-tunnel-url/poster/{poster-id}

# Check OG tags
curl https://your-tunnel-url/poster/{poster-id} | grep "og:"
```

## Still Not Working?

1. **Check browser console** for errors
2. **Check network tab** - verify image URL loads
3. **Test image URL directly** - should return image, not 404
4. **Use Facebook Sharing Debugger** - it shows specific errors
5. **Verify tunnel is accessible** - visit tunnel URL in browser
6. **Check backend logs** - look for errors in share endpoint

## Need Help?

1. Check `FACEBOOK_SHARING_IMPLEMENTATION.md` for full documentation
2. Review `QUICK_START_FACEBOOK_SHARING.md` for setup steps
3. Verify all environment variables are set correctly



