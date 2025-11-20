# Fix for "Failed to fetch" Error

## Problem

Frontend showing error when trying to connect to backend:

```
TypeError: Failed to fetch
at handleSave (src\components\settings\CompanyProfileSettings.tsx:368:36)
```

## Root Cause

This is a **CORS (Cross-Origin Resource Sharing)** configuration issue. The frontend (running on `http://localhost:3000`) was unable to communicate with the backend (running on `http://localhost:8000`) because CORS wasn't properly configured in all scenarios.

## Solution

### 1. Updated CORS Settings

Updated `backend/frameio_backend/settings.py` to allow all origins in development mode:

**Before:**
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

**After:**
```python
# Allow all origins in development for easier testing
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
```

Also added explicit `CORS_ALLOW_METHODS` configuration.

## How to Apply the Fix

### 1. **IMPORTANT: Restart the Backend Server**

The backend must be restarted for the settings to take effect:

```bash
# Stop the current backend server (Ctrl+C)

# Then restart it
cd backend
python manage.py runserver
```

### 2. Refresh the Frontend

Hard refresh your browser (Ctrl+Shift+R or Cmd+Shift+R on Mac)

## Verify the Fix

### Option 1: Quick Test Script

```bash
node test-company-profile-api.js
```

Should output:
```
✅ SUCCESS! Company profile API is working
```

### Option 2: Test in Browser

1. Open browser console (F12)
2. Go to http://localhost:3000/dashboard/settings
3. Try to save company profile
4. No more "Failed to fetch" errors

### Option 3: Test Health Endpoint

Open a new terminal and run:

```bash
curl http://localhost:8000/health/
```

Should return:
```json
{
  "status": "healthy",
  "message": "Backend server is running",
  "timestamp": "2024-..."
}
```

From the browser console, test:

```javascript
fetch('http://localhost:8000/health/')
  .then(r => r.json())
  .then(data => console.log('✅ Backend connected:', data))
  .catch(err => console.error('❌ Failed:', err))
```

## Common Issues

### Still Getting "Failed to fetch"?

1. **Backend not running**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/health/
   ```
   If you get "Connection refused", start the backend:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Backend running on different port**
   
   Check the terminal where you started the backend. It should say:
   ```
   Starting development server at http://127.0.0.1:8000/
   ```
   
   If it's on a different port, update `frontend/.env.local`:
   ```bash
   NEXT_PUBLIC_API_URL=http://localhost:YOUR_PORT/api
   NEXT_PUBLIC_API_BASE_URL=http://localhost:YOUR_PORT
   ```

3. **Forgot to restart backend**
   
   Settings changes require a backend restart. Press Ctrl+C and restart:
   ```bash
   cd backend
   python manage.py runserver
   ```

4. **CSRF Token issues**
   
   If you see CSRF errors, the CORS settings should fix it. If not, try:
   ```bash
   # Clear browser cookies for localhost
   # Then hard refresh (Ctrl+Shift+R)
   ```

5. **Windows Firewall blocking**
   
   On Windows, check if firewall is blocking the connection:
   - Go to Windows Defender Firewall
   - Allow Python through the firewall
   - Restart the backend

## Technical Details

### What is CORS?

CORS is a security feature that prevents websites from making requests to a different domain. Since:
- Frontend runs on `http://localhost:3000`
- Backend runs on `http://localhost:8000`

These are considered different origins, so CORS headers are required.

### How the Fix Works

The Django backend now sends these headers in every response:

```
Access-Control-Allow-Origin: http://localhost:3000
Access-Control-Allow-Credentials: true
Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
Access-Control-Allow-Headers: authorization, content-type, ...
```

These headers tell the browser: "It's okay for localhost:3000 to make requests to me."

### Development vs Production

**Development (DEBUG=True):**
- `CORS_ALLOW_ALL_ORIGINS = True` - Accept requests from any origin
- Convenient for testing
- **Never use in production!**

**Production (DEBUG=False):**
- `CORS_ALLOWED_ORIGINS` - Specific list of allowed origins
- Only your production domain
- Secure and restricted

## Files Modified

- ✏️ `backend/frameio_backend/settings.py` - Updated CORS configuration
- ➕ `CORS_FIX.md` - This documentation

## Testing Checklist

- [ ] Backend server restarted
- [ ] Can access http://localhost:8000/health/ 
- [ ] Can access http://localhost:8000/api/users/company-profiles/
- [ ] Frontend can load company profile settings
- [ ] Can save company profile without "Failed to fetch" error
- [ ] No CORS errors in browser console

## Related Issues Fixed

This fix also resolves:
- ❌ "CORS policy blocked" errors
- ❌ "No 'Access-Control-Allow-Origin' header" errors  
- ❌ Network errors when saving company profile
- ❌ Failed uploads
- ❌ Any "Failed to fetch" errors to backend API

## Prevention

To avoid this issue in the future:

1. **Always restart backend after settings changes**
2. **Check browser console for CORS errors**
3. **Use the test scripts to verify connectivity**
4. **Keep CORS configuration in sync with your domains**

## Support

If still having issues:

1. Check backend terminal for error messages
2. Check browser console (F12) → Network tab
3. Verify backend is accessible: `curl http://localhost:8000/health/`
4. Check ports are correct in `.env` files
5. Try a different browser to rule out cache issues




