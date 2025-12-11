# Frontend Setup Guide - Same Server Deployment

This guide helps you set up the Next.js frontend on the same server as the backend.

## Prerequisites

- Backend is already running and working
- Node.js and npm are installed
- Nginx is configured

## Step 1: Build Next.js Frontend

```bash
# Navigate to frontend directory
cd ~/Frameio/frontend

# Install dependencies (if not already done)
npm install

# Set production environment variable
export NODE_ENV=production
export NEXT_PUBLIC_API_URL=http://13.213.53.199/api

# Build Next.js application
npm run build

# This creates the .next/ directory with production build
```

## Step 2: Install PM2 (Process Manager)

PM2 will keep Next.js running in the background:

```bash
# Install PM2 globally
sudo npm install -g pm2

# Verify installation
pm2 --version
```

## Step 3: Start Next.js with PM2

```bash
cd ~/Frameio/frontend

# Start Next.js in production mode
pm2 start npm --name "frameio-frontend" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the command it outputs (usually something like: sudo env PATH=... pm2 startup systemd -u ubuntu --hp /home/ubuntu)
```

## Step 4: Verify Next.js is Running

```bash
# Check PM2 status
pm2 status

# Check if Next.js is listening on port 3000
sudo netstat -tulpn | grep :3000

# View PM2 logs
pm2 logs frameio-frontend

# Test Next.js directly
curl http://127.0.0.1:3000
```

## Step 5: Update Nginx Configuration

The nginx.conf file has already been updated. Now copy it to the server:

```bash
cd ~/Frameio

# Copy updated nginx config
sudo cp nginx.conf /etc/nginx/sites-available/frameio

# Test Nginx configuration
sudo nginx -t

# If test passes, reload Nginx
sudo systemctl reload nginx
```

## Step 6: Test Everything

```bash
# Test frontend
curl http://13.213.53.199/

# Test API (should still work)
curl http://13.213.53.199/api/

# Test admin (should still work)
curl http://13.213.53.199/admin/
```

## Step 7: Access in Browser

Open in your browser:
- **Frontend:** `http://13.213.53.199/`
- **API:** `http://13.213.53.199/api/`
- **Admin:** `http://13.213.53.199/admin/`

## PM2 Management Commands

```bash
# View status
pm2 status

# View logs
pm2 logs frameio-frontend

# Restart frontend
pm2 restart frameio-frontend

# Stop frontend
pm2 stop frameio-frontend

# Start frontend
pm2 start frameio-frontend

# Delete from PM2
pm2 delete frameio-frontend

# Monitor (real-time)
pm2 monit
```

## Alternative: Systemd Service (Instead of PM2)

If you prefer systemd over PM2, create a service file:

```bash
sudo nano /etc/systemd/system/frameio-frontend.service
```

Paste this:

```ini
[Unit]
Description=Frameio Next.js Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Frameio/frontend
Environment="NODE_ENV=production"
Environment="NEXT_PUBLIC_API_URL=http://13.213.53.199/api"
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service
sudo systemctl enable frameio-frontend.service

# Start service
sudo systemctl start frameio-frontend.service

# Check status
sudo systemctl status frameio-frontend.service
```

## Troubleshooting

### Frontend not loading

1. **Check if Next.js is running:**
   ```bash
   pm2 status
   # OR
   sudo systemctl status frameio-frontend.service
   ```

2. **Check if port 3000 is listening:**
   ```bash
   sudo netstat -tulpn | grep :3000
   ```

3. **Check Next.js logs:**
   ```bash
   pm2 logs frameio-frontend
   # OR
   sudo journalctl -u frameio-frontend.service -n 50
   ```

4. **Test Next.js directly:**
   ```bash
   curl http://127.0.0.1:3000
   ```

### Nginx 502 Bad Gateway

This means Nginx can't reach Next.js:

1. **Check if Next.js is running on port 3000**
2. **Check Nginx error logs:**
   ```bash
   sudo tail -20 /var/log/nginx/error.log
   ```
3. **Verify upstream in Nginx config:**
   ```bash
   sudo grep -A 2 "upstream nextjs" /etc/nginx/sites-available/frameio
   ```

### Frontend shows API errors

Make sure the frontend environment variable is set:

```bash
# Check environment variable
cd ~/Frameio/frontend
echo $NEXT_PUBLIC_API_URL

# If not set, restart with environment variable
pm2 delete frameio-frontend
NEXT_PUBLIC_API_URL=http://13.213.53.199/api pm2 start npm --name "frameio-frontend" -- start
pm2 save
```

## Updating Frontend

When you update the frontend code:

```bash
cd ~/Frameio/frontend

# Pull latest changes (if using git)
git pull

# Install new dependencies (if any)
npm install

# Rebuild
npm run build

# Restart PM2
pm2 restart frameio-frontend

# OR if using systemd
sudo systemctl restart frameio-frontend.service
```

## Environment Variables

Create a `.env.local` file in the frontend directory:

```bash
cd ~/Frameio/frontend
nano .env.local
```

Add:
```env
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://13.213.53.199/api
NEXT_PUBLIC_APP_URL=http://13.213.53.199
```

Then restart the frontend service.

## Complete Setup Checklist

- [ ] Node.js and npm installed
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend built (`npm run build`)
- [ ] PM2 installed and Next.js started
- [ ] Next.js running on port 3000
- [ ] Nginx config updated and reloaded
- [ ] Frontend accessible at `http://13.213.53.199/`
- [ ] API still accessible at `http://13.213.53.199/api/`
- [ ] Admin still accessible at `http://13.213.53.199/admin/`

## Summary

Your setup should now have:
- **Frontend (Next.js):** Running on port 3000, proxied by Nginx
- **Backend (Django/Gunicorn):** Running on port 8000, proxied by Nginx
- **Nginx:** Routing:
  - `/` → Next.js (port 3000)
  - `/api/` → Django (port 8000)
  - `/admin/` → Django (port 8000)
  - `/static/` → Django static files
  - `/media/` → Django media files

Everything should be accessible through `http://13.213.53.199/`!

