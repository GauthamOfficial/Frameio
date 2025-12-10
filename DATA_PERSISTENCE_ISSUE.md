# Data Persistence Issue - Posters and Brandkits Disappearing

## Problem
After signing in to a previous account, generated posters and brandkits from the dashboard are gone.

## Root Cause
The backend filters posters and brandkits by:
1. **User ID** - The Django user associated with the poster/brandkit
2. **Organization** - The organization context

If the Clerk user isn't properly synced with the Django backend user, or if the organization context is different, the data won't appear.

## Why This Happens

### 1. User Sync Issue
When you sign in with Clerk, the frontend should automatically sync your Clerk user to the Django backend. If this sync fails or creates a new user record instead of using the existing one, your data won't be associated with the "new" user.

### 2. Organization Context Mismatch
Posters and brandkits are filtered by organization. If:
- Your previous data was created with a different organization
- The organization context isn't being set correctly
- You're in a different organization now

Then the data won't show up.

### 3. Clerk ID Mismatch
If your Clerk user ID changed or isn't matching the `clerk_id` stored in the Django user record, the sync might create a duplicate user instead of using the existing one.

## How to Fix

### Step 1: Check User Sync
1. Open browser DevTools (F12)
2. Go to Console tab
3. Look for messages about user sync when you sign in
4. Check if there are any errors

### Step 2: Verify Backend User
1. Check your Django admin panel or backend logs
2. Verify that your Clerk user is synced to the Django backend
3. Check if there are multiple user records with the same email

### Step 3: Check Organization Context
1. Check browser console for organization-related logs
2. Verify `X-Organization` or `X-Dev-Org-ID` headers are being sent
3. Check if your user has the correct organization association

### Step 4: Manual Fix (If Needed)
If your data exists but isn't showing:

1. **Check Database Directly:**
   ```python
   # In Django shell
   from ai_services.models import GeneratedPoster, GeneratedBrandingKit
   from users.models import User
   
   # Find your user
   user = User.objects.get(email='your-email@example.com')
   
   # Check posters
   posters = GeneratedPoster.objects.filter(user=user)
   print(f"Found {posters.count()} posters for user")
   
   # Check brandkits
   brandkits = GeneratedBrandingKit.objects.filter(user=user)
   print(f"Found {brandkits.count()} brandkits for user")
   ```

2. **Re-associate Data:**
   If data exists but isn't associated with your user:
   ```python
   # Find posters/brandkits without user association
   orphaned_posters = GeneratedPoster.objects.filter(user__isnull=True)
   orphaned_brandkits = GeneratedBrandingKit.objects.filter(user__isnull=True)
   
   # Associate them with your user (if they're yours)
   # BE CAREFUL - only do this if you're sure they belong to you
   # orphaned_posters.update(user=user)
   ```

## Prevention

### Ensure Proper User Sync
The `useAuth` hook should automatically sync users when they sign in. Make sure:
- The sync endpoint `/api/users/sync_from_clerk/` is working
- The `clerk_id` matches between Clerk and Django
- No duplicate users are created

### Check Organization Context
Make sure:
- Organization headers are being sent with API requests
- Your user has the correct organization membership
- The organization context is consistent across sessions

## Quick Check

Run this in your browser console after signing in:
```javascript
// Check if user is synced
fetch('/api/users/')
  .then(r => r.json())
  .then(data => {
    console.log('Current user:', data);
    console.log('User ID:', data[0]?.id);
    console.log('Clerk ID:', data[0]?.clerk_id);
    console.log('Organization:', data[0]?.current_organization);
  });
```

## Next Steps

1. **Check browser console** for sync errors
2. **Verify backend logs** for user sync messages
3. **Check database** to see if data exists but isn't associated
4. **Contact support** if data is truly missing (not just filtered)

## Important Note

**This is NOT normal behavior.** Your data should persist across sign-ins. If posters and brandkits are truly gone (not just hidden by filters), this indicates a serious issue that needs to be investigated.

