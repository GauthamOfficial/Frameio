# Deploy Frontend Changes to Server

This guide will help you deploy the frontend URL fixes to your production server.

## Option 1: Using Git (Recommended if you have Git on server)

### Step 1: Commit and Push Changes Locally

```bash
# From your local machine, commit the changes
git add frontend/src/
git commit -m "Fix API URL construction to prevent double /api/api/ paths"
git push origin main  # or your branch name
```

### Step 2: SSH to Your Server

```bash
ssh ubuntu@13.213.53.199
# or
ssh your-username@13.213.53.199
```

### Step 3: Pull Changes and Deploy

```bash
# Navigate to project directory
cd /opt/frameio

# Pull latest changes
git pull origin main  # or your branch name

# Navigate to frontend directory
cd frontend

# Install dependencies (if package.json changed)
npm install

# Build the Next.js application
npm run build

# Restart the frontend service
# If using PM2:
pm2 restart frameio-frontend

# Or if using systemd/service:
sudo systemctl restart frameio-frontend

# Or if running manually, stop and restart:
# pkill -f "next start"
# npm start &
```

## Option 2: Manual File Upload (If not using Git)

### Step 1: Upload Changed Files

You can use SCP, SFTP, or any file transfer tool to upload the changed files:

**Files that were changed:**
- `frontend/src/lib/config.ts`
- `frontend/src/components/lazy/enhanced-poster-generator-with-branding.tsx`
- `frontend/src/hooks/useAuth.ts`
- `frontend/src/components/settings/CompanyProfileSettings.tsx`
- `frontend/src/app/api/users/me/route.ts`
- `frontend/src/app/api/admin/users/route.ts`
- `frontend/src/app/api/admin/users/[id]/route.ts`
- `frontend/src/app/api/admin/analytics/route.ts`
- `frontend/src/utils/api.ts` (new buildApiUrl function)

**Using SCP from your local machine:**

```bash
# Upload individual files
scp frontend/src/lib/config.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/lib/
scp frontend/src/utils/api.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/utils/
scp frontend/src/hooks/useAuth.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/hooks/
scp frontend/src/components/lazy/enhanced-poster-generator-with-branding.tsx ubuntu@13.213.53.199:/opt/frameio/frontend/src/components/lazy/
scp frontend/src/components/settings/CompanyProfileSettings.tsx ubuntu@13.213.53.199:/opt/frameio/frontend/src/components/settings/
scp frontend/src/app/api/users/me/route.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/app/api/users/me/
scp frontend/src/app/api/admin/users/route.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/app/api/admin/users/
scp frontend/src/app/api/admin/users/[id]/route.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/app/api/admin/users/[id]/
scp frontend/src/app/api/admin/analytics/route.ts ubuntu@13.213.53.199:/opt/frameio/frontend/src/app/api/admin/analytics/
```

**Or upload the entire src directory:**

```bash
scp -r frontend/src ubuntu@13.213.53.199:/opt/frameio/frontend/
```

### Step 2: SSH to Server and Build

```bash
# SSH to server
ssh ubuntu@13.213.53.199

# Navigate to frontend
cd /opt/frameio/frontend

# Install dependencies (if needed)
npm install

# Build the application
npm run build

# Restart the frontend service
pm2 restart frameio-frontend
# OR
sudo systemctl restart frameio-frontend
```

## Option 3: Using the Deployment Script

If you have the deployment script set up:

```bash
# SSH to server
ssh ubuntu@13.213.53.199

# Navigate to deployment directory
cd /opt/frameio/deployment

# Run deployment script (this will handle both backend and frontend)
sudo ./deploy.sh
```

## Quick Deploy Script (Frontend Only)

Create a quick deploy script on your server:

```bash
# SSH to server
ssh ubuntu@13.213.53.199

# Create deploy script
cat > /opt/frameio/deploy-frontend.sh << 'EOF'
#!/bin/bash
cd /opt/frameio/frontend
echo "Installing dependencies..."
npm install
echo "Building Next.js application..."
npm run build
echo "Restarting frontend..."
pm2 restart frameio-frontend || systemctl restart frameio-frontend
echo "Frontend deployment complete!"
EOF

# Make it executable
chmod +x /opt/frameio/deploy-frontend.sh

# Run it
sudo /opt/frameio/deploy-frontend.sh
```

## Verify Deployment

After deployment, verify the changes are working:

1. **Check if the build was successful:**
   ```bash
   # On server
   ls -la /opt/frameio/frontend/.next
   ```

2. **Check frontend service status:**
   ```bash
   # If using PM2
   pm2 status frameio-frontend
   pm2 logs frameio-frontend
   
   # If using systemd
   sudo systemctl status frameio-frontend
   ```

3. **Test the endpoints in browser:**
   - Open browser developer tools (F12)
   - Go to Network tab
   - Try generating an image or saving a profile
   - Check that requests go to correct URLs (no double `/api/api/`)
   - URLs should be like: `http://13.213.53.199/api/users/sync_from_clerk/`
   - NOT like: `http://13.213.53.199/api/api/users/sync_from_clerk/`

4. **Check browser console for errors:**
   - Open browser console (F12)
   - Look for any 404 errors
   - All API calls should return 200 OK or proper error codes (not 404)

## Troubleshooting

### Build Fails

```bash
# Clear Next.js cache and rebuild
cd /opt/frameio/frontend
rm -rf .next
npm run build
```

### Service Won't Start

```bash
# Check logs
pm2 logs frameio-frontend
# OR
sudo journalctl -u frameio-frontend -f

# Check if port is in use
sudo netstat -tulpn | grep :3000
```

### Still Getting 404 Errors

1. **Verify the build includes your changes:**
   ```bash
   # On server, check if buildApiUrl function exists
   grep -r "buildApiUrl" /opt/frameio/frontend/.next
   ```

2. **Clear browser cache:**
   - Hard refresh: Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

3. **Check environment variables:**
   ```bash
   # On server
   cat /opt/frameio/frontend/.env.local
   # Make sure NEXT_PUBLIC_API_URL is set correctly
   ```

4. **Verify API_BASE_URL in production:**
   - Should be: `http://13.213.53.199/api`
   - Check: `frontend/src/utils/api.ts` line 10

## Environment Variables

Make sure your production environment has:

```bash
# In /opt/frameio/frontend/.env.local or .env.production
NEXT_PUBLIC_API_URL=http://13.213.53.199/api
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_key
NEXT_PUBLIC_CLERK_FRONTEND_API=your_api_url
```

## Summary

The fastest way to deploy:

1. **If using Git:**
   ```bash
   git pull && cd frontend && npm run build && pm2 restart frameio-frontend
   ```

2. **If not using Git:**
   ```bash
   # Upload files via SCP/SFTP, then:
   cd /opt/frameio/frontend && npm install && npm run build && pm2 restart frameio-frontend
   ```

After deployment, test the endpoints to ensure 404 errors are resolved!

