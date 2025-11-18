# Fix for "Permission denied" Error

## Problem

When trying to save company profile, you get this error:

```
Permission denied. You do not have access to save this profile. 
Please contact support if this persists.
```

## Root Cause

The backend authentication system requires at least one user in the database. When the database is empty, authentication fails and returns 403 Forbidden.

## Solution

Create a test user in the database. There are two methods:

### Method 1: Automatic Script (Recommended)

Run this simple Python script:

```bash
cd backend
python create_test_user.py
```

**Output should be:**
```
✅ Created test user successfully!
   Email: test@example.com
   Username: testuser
   ID: 1
   
   You can now use the app without permission errors!
```

### Method 2: Django Management Command

```bash
cd backend
python manage.py shell
```

Then in the Python shell:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

print(f"Created user: {user.email}")
```

Press `Ctrl+D` or type `exit()` to exit the shell.

### Method 3: Django Admin (Creates Superuser)

```bash
cd backend
python manage.py createsuperuser
```

Follow the prompts to create an admin user with full privileges.

## Verify the Fix

### 1. Check User Exists

```bash
cd backend
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()
print(f"Total users: {User.objects.count()}")
if User.objects.exists():
    user = User.objects.first()
    print(f"First user: {user.email}")
```

### 2. Test Company Profile

1. Go to http://localhost:3000/dashboard/settings
2. Try to save company profile
3. ✅ Should save successfully (no more "Permission denied" error!)

### 3. Check Backend Logs

When you save, the backend should log:

```
INFO Development Clerk auth: Using user test@example.com with token test_clerk...
INFO CompanyProfileViewSet.create: Creating profile for user test@example.com
```

## How It Works

### Development Authentication Flow

1. Frontend sends request with `Authorization: Bearer test_clerk_token`
2. Backend `ClerkAuthentication` receives the token
3. In DEBUG mode, accepts `test_clerk_token`
4. Looks for first user in database: `User.objects.first()`
5. Returns that user for the request
6. Request proceeds with authenticated user
7. Company profile is saved successfully

### Why This Error Happened

The authentication code tries to get the first user:

```python
user = User.objects.first()
if not user:
    # Try to create default user
    user = User.objects.create_user(...)
```

However, if user creation fails or was skipped, authentication returns `None`, causing the 403 error.

## Common Issues

### ❌ "No module named 'django'"

Make sure you're in the backend directory and virtual environment is activated:

```bash
# Activate virtual environment first
startup_env\Scripts\activate  # Windows
# or
source startup_env/bin/activate  # Mac/Linux

# Then run the script
cd backend
python create_test_user.py
```

### ❌ "django.db.utils.OperationalError: no such table"

Run migrations first:

```bash
cd backend
python manage.py migrate
python create_test_user.py
```

### ❌ Still getting "Permission denied" after creating user

1. **Restart backend server** - Stop (Ctrl+C) and restart:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Clear browser cache** - Hard refresh (Ctrl+Shift+R)

3. **Check backend logs** - Look for authentication errors in terminal

4. **Verify user exists**:
   ```bash
   cd backend
   python manage.py shell
   ```
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   print(User.objects.count())  # Should be > 0
   ```

### ❌ "Authentication required" instead of "Permission denied"

This means the token is not being sent. Check:

1. **Frontend is getting token** - Check browser console for:
   ```
   Using token: Present
   ```

2. **Clerk is configured** - If using Clerk, check environment variables

3. **Test token fallback works** - In development, should use `test_clerk_token`

## Prevention

### Always Create Test Data After Migrations

After running `python manage.py migrate`, create a test user:

```bash
python create_test_user.py
```

Or add to your setup script:

```bash
# backend/setup.sh
python manage.py migrate
python create_test_user.py
python manage.py runserver
```

### Use Django Fixtures

Create a fixture file `backend/users/fixtures/test_users.json`:

```json
[
  {
    "model": "auth.user",
    "pk": 1,
    "fields": {
      "username": "testuser",
      "email": "test@example.com",
      "password": "pbkdf2_sha256$...",
      "first_name": "Test",
      "last_name": "User"
    }
  }
]
```

Load with:
```bash
python manage.py loaddata test_users
```

## Production Considerations

This fix is **only for development**. In production:

1. **Never use test tokens** - Always use real Clerk JWT tokens
2. **Users register normally** - Through Clerk OAuth or email/password
3. **No default users** - Users are created through registration flow
4. **Proper JWT validation** - Use Clerk's backend SDK

## Files Created

- ➕ `backend/create_test_user.py` - Script to create test user
- ➕ `PERMISSION_DENIED_FIX.md` - This documentation

## Related Documentation

- [CLERK_403_FIX.md](CLERK_403_FIX.md) - Fix for 403 errors
- [CORS_FIX.md](CORS_FIX.md) - Fix for CORS issues
- [CLERK_AUTH_FIX_SUMMARY.md](CLERK_AUTH_FIX_SUMMARY.md) - Complete auth setup

## Testing Checklist

After creating a user:

- [ ] User exists in database
- [ ] Backend server is running
- [ ] Frontend can access /dashboard/settings
- [ ] Can save company profile without error
- [ ] Backend logs show authentication success
- [ ] No 403 or 401 errors in browser console

---

**TLDR**: 
1. Run `cd backend && python create_test_user.py`
2. Restart backend if needed
3. Try saving company profile again
4. Should work! ✅

