# Authentication Fix for Company Profile Settings

## Problem
The settings page was showing "You do not have permission to perform this action" errors because authentication was failing.

## Root Cause
1. `ClerkAuthentication` was returning `None` immediately if `CLERK_SECRET_KEY` was not set, even in DEBUG mode
2. The authentication wasn't properly handling the `test_clerk_token` in development
3. No user was being returned even when a token was provided

## Fixes Applied

### 1. Updated `ClerkAuthentication.authenticate()` (backend/users/authentication.py)
- Now works in DEBUG mode even without `CLERK_SECRET_KEY`
- Added better logging to track authentication attempts
- Doesn't raise exceptions in DEBUG mode, allowing fallback authentication

### 2. Updated `ClerkAuthentication.validate_clerk_token()` (backend/users/authentication.py)
- Now accepts `test_clerk_token` or any token in DEBUG mode
- Automatically creates a default development user if no users exist
- Better error handling and logging

### 3. Added logging to `CompanyProfileViewSet` (backend/users/views.py)
- Added `initial()` method to log authentication status
- Helps debug permission issues by showing when authentication fails

## Testing

1. **Restart your backend server** to apply the changes:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Check the backend logs** when you access the settings page. You should see:
   - `ClerkAuthentication: Successfully authenticated user test@example.com`
   - `CompanyProfileViewSet: User test@example.com authenticated for GET /api/users/company-profiles/`

3. **If you still see permission errors**, check:
   - Backend logs for authentication warnings
   - Browser console for the exact error message
   - Network tab to see the response status code

## Expected Behavior

After these fixes:
- ✅ The settings page should load without permission errors
- ✅ You should be able to save profile details
- ✅ Authentication should work with `test_clerk_token` in development
- ✅ Backend logs will show detailed authentication information

## If Issues Persist

1. Check backend logs for authentication warnings
2. Verify the user exists: `python manage.py shell -c "from django.contrib.auth import get_user_model; print(get_user_model().objects.count())"`
3. Check if the token is being sent: Look for `Authorization: Bearer test_clerk_token` in network requests
4. Verify DEBUG mode is enabled in Django settings




