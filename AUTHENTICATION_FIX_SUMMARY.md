# Authentication 403 Error - Complete Fix Guide

## Problem Diagnosed

The 403 error occurs because:
1. ✅ Backend is running
2. ✅ Database is connected  
3. ✅ Test user exists (`test@example.com`)
4. ✅ Authentication classes are configured
5. ❌ **Backend server needs restart to apply auth changes**

## Error Messages

- **Without auth**: "Authentication credentials were not provided"
- **With auth**: "You do not have permission to perform this action"

This means authentication IS working but needs a server restart!

## SOLUTION

### Step 1: Stop the Backend Server

In your backend terminal:
```
Press Ctrl+C
```

### Step 2: Restart the Backend Server

```bash
cd backend
python manage.py runserver
```

### Step 3: Test the Fix

Run this command:
```bash
node test-direct-auth.js
```

Expected output should be **200 OK** instead of 403.

### Step 4: Test in Frontend

Refresh your frontend and try saving the company profile again.

## What Was Fixed

1. ✅ **Authentication Code Updated** (`backend/users/authentication.py`):
   - `DevelopmentAuthentication` now handles `test_clerk_token`
   - Auto-creates test user if database is empty
   - Falls back gracefully when Clerk is not configured

2. ✅ **Database Setup** (`backend/fix_auth_database.py`):
   - Test user created: `test@example.com`
   - User ID: `97e36ced-7160-472d-ab5c-77cd2b4e8480`
   - Password: `testpass123`

3. ✅ **Frontend Error Handling** (`frontend/src/components/settings/CompanyProfileSettings.tsx`):
   - Improved error logging
   - Non-blocking health checks
   - Better 403 error messages

4. ✅ **API Configuration** (`frontend/src/lib/config.ts`):
   - Supports relative URLs (Next.js proxy)
   - Handles empty API_BASE_URL gracefully

## Authentication Flow

```
Frontend Request → Authorization: Bearer test_clerk_token
      ↓
Backend: DevelopmentAuthentication.authenticate()
      ↓
Check token == 'test_clerk_token' → Get/Create User
      ↓
Return (user, None) → Set request.user
      ↓
IsAuthenticated Permission Check
      ↓
✅ Allow Access
```

## Verification

After restarting the server, verify with:

```bash
# Test 1: Health check
curl http://localhost:8000/health/

# Test 2: Company profiles (should work now)
curl -H "Authorization: Bearer test_clerk_token" \
     http://localhost:8000/api/users/company-profiles/
```

## Troubleshooting

### If still getting 403:

1. **Check backend logs** for authentication messages:
   ```
   INFO: Development auth (test_clerk_token): Using user test@example.com
   ```

2. **Verify DEBUG mode** in `backend/.env`:
   ```
   DEBUG=True
   ```

3. **Check user exists**:
   ```bash
   cd backend
   python manage.py shell
   >>> from django.contrib.auth import get_user_model
   >>> User = get_user_model()
   >>> user = User.objects.filter(email='test@example.com').first()
   >>> print(f"User: {user.email}, Active: {user.is_active}")
   >>> exit()
   ```

4. **Verify authentication classes** in `backend/frameio_backend/settings.py`:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': [
           'users.authentication.DevelopmentAuthentication',  # Must be first!
           'rest_framework.authentication.SessionAuthentication',
           'users.authentication.ClerkAuthentication',
       ],
   }
   ```

## Files Modified

- ✅ `backend/users/authentication.py` - Enhanced authentication
- ✅ `frontend/src/components/settings/CompanyProfileSettings.tsx` - Better error handling
- ✅ `frontend/src/lib/config.ts` - Improved API configuration
- ✅ `backend/fix_auth_database.py` - Database setup script
- ✅ `fix-auth-issue.js` - Diagnostic script
- ✅ `test-direct-auth.js` - Authentication test script

## Next Steps

1. **Restart backend server** (most important!)
2. Test with diagnostic scripts
3. Try saving company profile in frontend
4. Monitor backend logs for any issues

## Success Indicators

✅ Test scripts return 200 OK
✅ Backend logs show "Development auth" messages  
✅ Frontend can save/load company profiles
✅ No more 403 errors in browser console

---

**Note**: In production, replace `test_clerk_token` with real Clerk JWT tokens. The `DevelopmentAuthentication` class only works when `DEBUG=True`.





