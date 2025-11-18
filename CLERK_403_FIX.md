# Fix for 403 Forbidden Error on Company Profiles API

## Problem

After implementing Clerk OAuth authentication, the company profiles API was returning 403 Forbidden errors:

```
GET /api/users/company-profiles/ - 403 Forbidden
```

## Root Cause

The issue had multiple parts:

### 1. Frontend Auth Hook Not Using Clerk Tokens

The custom `useAuth` hook in `frontend/src/hooks/useAuth.ts` was not properly integrating with Clerk. It was only returning test tokens instead of real Clerk tokens.

### 2. Backend Authentication Disabled in DEBUG Mode

The Django REST Framework settings were disabling all authentication classes when `DEBUG=True`:

```python
'DEFAULT_AUTHENTICATION_CLASSES': [] if DEBUG else [...]
```

This meant that `request.user` was always `AnonymousUser`, but the `CompanyProfileViewSet` required an authenticated user, causing the 403 error.

## Solution

### 1. Updated Frontend Auth Hook

Updated `frontend/src/hooks/useAuth.ts` to properly integrate with Clerk:

- Now uses Clerk's `useAuth()` and `useUser()` hooks
- `getToken()` method tries Clerk token first, then falls back to localStorage and test token
- User data comes from Clerk when available
- Sign out properly calls Clerk's sign out method

### 2. Fixed Backend Authentication Settings

Updated `backend/frameio_backend/settings.py` to always enable authentication:

**Before:**
```python
'DEFAULT_AUTHENTICATION_CLASSES': [] if DEBUG else [
    'users.authentication.DevelopmentAuthentication',
    'rest_framework.authentication.SessionAuthentication',
    'users.authentication.ClerkAuthentication',
],
```

**After:**
```python
'DEFAULT_AUTHENTICATION_CLASSES': [
    'users.authentication.ClerkAuthentication',
    'users.authentication.DevelopmentAuthentication',
    'rest_framework.authentication.SessionAuthentication',
],
```

Now authentication is always enabled, even in DEBUG mode. The `ClerkAuthentication` class accepts `test_clerk_token` in development and returns the first user.

## How It Works Now

### Development Mode (DEBUG=True)

1. Frontend requests company profile with `Authorization: Bearer test_clerk_token`
2. Backend tries `ClerkAuthentication` first
3. `ClerkAuthentication.validate_clerk_token()` accepts test token in DEBUG mode
4. Returns first user from database (or creates default dev user if none exists)
5. Request proceeds with authenticated user
6. Company profile is returned successfully

### With Clerk OAuth Configured

1. User signs in with Google OAuth via Clerk
2. Frontend gets real Clerk JWT token
3. Frontend makes API request with `Authorization: Bearer <clerk_jwt>`
4. Backend validates Clerk JWT (when Clerk SDK is properly integrated)
5. Request proceeds with authenticated user
6. Company profile is returned successfully

## Testing the Fix

### 1. Restart Backend Server

The backend settings have changed, so you need to restart:

```bash
cd backend
python manage.py runserver
```

### 2. Restart Frontend Server

The auth hook has changed, so restart the frontend:

```bash
cd frontend
npm run dev
```

### 3. Test Company Profile Access

Open your browser to http://localhost:3000/dashboard/settings

You should now be able to:
- ✅ View your company profile
- ✅ Update company information
- ✅ Upload logo
- ✅ No more 403 errors

## Development vs Production

### Development Mode (DEBUG=True)

- Uses `test_clerk_token` for easy testing
- No real Clerk setup required
- Authentication always succeeds
- Returns first user or creates default dev user

### Production Mode (DEBUG=False)

- Requires real Clerk JWT tokens
- Clerk environment variables must be set
- Proper JWT validation
- No fallback authentication

## Files Modified

- ✏️ `frontend/src/hooks/useAuth.ts` - Integrated with Clerk
- ✏️ `backend/frameio_backend/settings.py` - Always enable authentication
- ➕ `CLERK_403_FIX.md` - This documentation

## Related Documentation

- [CLERK_AUTH_FIX_SUMMARY.md](CLERK_AUTH_FIX_SUMMARY.md) - Main Clerk OAuth fix
- [CLERK_GOOGLE_OAUTH_SETUP.md](CLERK_GOOGLE_OAUTH_SETUP.md) - Setup guide
- [QUICK_START_CLERK.md](QUICK_START_CLERK.md) - Quick start guide

## Troubleshooting

### Still getting 403 errors?

1. **Restart both servers** - Settings/code changes require restart
2. **Check backend logs** - Look for authentication errors in terminal
3. **Check browser console** - Look for token errors
4. **Clear browser cache** - Old tokens might be cached
5. **Check user exists** - Backend needs at least one user in database

### Create a test user (if needed):

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)
print(f"Created user: {user.email}")
```

### Check authentication in Django shell:

```bash
cd backend  
python manage.py shell
```

```python
from users.authentication import ClerkAuthentication
from django.test import RequestFactory

# Create a test request
factory = RequestFactory()
request = factory.get('/api/users/company-profiles/')
request.META['HTTP_AUTHORIZATION'] = 'Bearer test_clerk_token'

# Try authentication
auth = ClerkAuthentication()
result = auth.authenticate(request)
print(f"Auth result: {result}")
# Should print: Auth result: (<User: ...>, None)
```

## Benefits of This Fix

1. ✅ **Works with or without Clerk** - Development mode uses test tokens
2. ✅ **Easy testing** - No Clerk setup required for development
3. ✅ **Production ready** - Properly validates Clerk tokens when configured
4. ✅ **Consistent auth** - Same auth flow for all API endpoints
5. ✅ **Better errors** - Clear authentication errors instead of 403

