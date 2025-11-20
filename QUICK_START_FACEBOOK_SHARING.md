# Quick Start: Facebook Sharing Setup

## ⚠️ Important: ngrok Requires Authentication

If you see this error:
```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
```

**Solution: Use Cloudflare Tunnel instead (No account required!)**

## 🚀 Recommended: Cloudflare Tunnel (No Auth Required)

### Option 1: Automatic Setup (Windows)

1. **Run the Cloudflare Tunnel script:**
   ```bash
   node start-cloudflare-tunnel.js
   ```
   
   This will:
   - Download Cloudflare Tunnel automatically
   - Start the tunnel
   - Display your public URL

2. **Copy the public URL** (e.g., `https://abc123.trycloudflare.com`)

3. **Set environment variable:**
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_APP_URL=https://abc123.trycloudflare.com
   ```

### Option 2: Manual Setup

1. **Download Cloudflare Tunnel:**
   ```bash
   # Windows PowerShell
   .\download-cloudflared.ps1
   
   # OR manually download from:
   # https://github.com/cloudflare/cloudflared/releases
   ```

2. **Start the tunnel:**
   ```bash
   cloudflared.exe tunnel --url http://localhost:3000
   ```

3. **Copy the URL** shown in the output (e.g., `https://abc123.trycloudflare.com`)

4. **Set environment variable:**
   ```bash
   NEXT_PUBLIC_APP_URL=https://abc123.trycloudflare.com
   ```

## 🔧 Alternative: ngrok (Requires Account)

If you prefer ngrok:

1. **Sign up:** https://dashboard.ngrok.com/signup
2. **Get authtoken:** https://dashboard.ngrok.com/get-started/your-authtoken
3. **Configure:**
   ```bash
   ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
   ```
4. **Start:**
   ```bash
   ngrok http 3000
   ```

## ✅ Testing

1. **Start your services:**
   ```bash
   # Terminal 1: Backend
   cd backend && python manage.py runserver
   
   # Terminal 2: Frontend
   cd frontend && npm run dev
   
   # Terminal 3: Tunnel (Cloudflare or ngrok)
   node start-cloudflare-tunnel.js
   # OR: ngrok http 3000
   ```

2. **Generate a poster** and note the poster ID

3. **Visit the poster page:**
   ```
   https://your-tunnel-url/poster/{poster-id}
   ```

4. **Test Facebook Sharing Debugger:**
   - Go to: https://developers.facebook.com/tools/debug/
   - Paste your poster URL
   - Click "Debug"
   - Verify preview shows correctly

5. **Test Share Button:**
   - Click "Share on Facebook" on the poster page
   - Verify popup opens with correct preview

## 🐛 Troubleshooting

### Tunnel URL not detected automatically?

**Solution:** Set `NEXT_PUBLIC_APP_URL` manually in your `.env.local`:
```bash
NEXT_PUBLIC_APP_URL=https://your-tunnel-url-here
```

### Facebook preview not showing?

1. **Check image URL is accessible:**
   ```bash
   curl -I https://your-image-url.jpg
   ```

2. **Force Facebook to re-scrape:**
   - Use Sharing Debugger: https://developers.facebook.com/tools/debug/
   - Click "Scrape Again"

3. **Verify OG tags:**
   - View page source
   - Check for `<meta property="og:image">` tag
   - Ensure image URL is absolute (starts with `http://` or `https://`)

### Cloudflare Tunnel not starting?

1. **Check if port 3000 is in use:**
   ```bash
   # Windows
   netstat -ano | findstr :3000
   
   # Linux/Mac
   lsof -i :3000
   ```

2. **Try manual download:**
   - Download from: https://github.com/cloudflare/cloudflared/releases
   - Extract and run: `cloudflared tunnel --url http://localhost:3000`

## 📝 Environment Variables

Create `frontend/.env.local`:
```bash
# Required
NEXT_PUBLIC_APP_URL=https://your-tunnel-url-here
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 🎯 Quick Commands

```bash
# Start Cloudflare Tunnel (Recommended)
node start-cloudflare-tunnel.js

# Start ngrok (if configured)
ngrok http 3000

# Test share endpoint
curl http://localhost:8000/api/ai/posters/{poster-id}/share/

# Test poster page
curl -I https://your-tunnel-url/poster/{poster-id}
```

## 💡 Tips

1. **Cloudflare Tunnel is free** and doesn't require authentication
2. **Tunnel URLs change** on each restart (unless using paid plan)
3. **Update `NEXT_PUBLIC_APP_URL`** after restarting tunnel
4. **Use Sharing Debugger** to verify OG tags before sharing



