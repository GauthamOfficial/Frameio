# Fix: Company Details Not Applied to Generated Posters

## Problem
Company details (logo, contact info) are not being included in generated posters even though the company profile is complete.

## Root Cause
The backend couldn't identify the correct user because the frontend wasn't sending the Clerk user email. Without the email, the backend would:
1. Try to authenticate but fail
2. Fall back to getting the first user (which might not have a company profile)
3. Result: Wrong user or no user → No company profile → No branding applied

## Solution Applied

### 1. Frontend Changes
**File:** `frontend/src/components/lazy/enhanced-poster-generator-with-branding.tsx`

Added Clerk user headers to the poster generation request:
- `X-CLERK-EMAIL` - Your email address (CRITICAL)
- `X-CLERK-ID` - Your Clerk user ID
- `X-CLERK-FIRST-NAME` - Your first name
- `X-CLERK-LAST-NAME` - Your last name

### 2. Backend Changes
**File:** `backend/ai_services/ai_poster_views.py`

Improved user lookup to prioritize Clerk email:
- First tries to find user by Clerk email (most reliable)
- Falls back to development headers
- Last resort: Gets first user with company profile (not recommended)

## How It Works Now

1. **Frontend** → Gets your Clerk user info from `useUser()` hook
2. **Frontend** → Sends request with:
   - `Authorization: Bearer <token>`
   - `X-CLERK-EMAIL: your@email.com` ← **This is the key!**
   - `X-CLERK-ID: user_xxxxx`
3. **Backend** → `ClerkAuthentication` receives headers
4. **Backend** → Finds user by email using `get_or_create_user_from_clerk()`
5. **Backend** → Gets user's company profile
6. **Backend** → Checks if `has_complete_profile == True`
7. **Backend** → If complete, applies branding via `BrandOverlayService`
8. **Result** → Poster includes your logo and contact info! ✅

## Testing

1. **Generate a poster**
2. **Check browser console** - You should see:
   ```
   📧 Sending Clerk email to backend: your@email.com
   ```

3. **Check backend logs** - You should see:
   ```
   ✅ Found user by Clerk email: your@email.com (ID: 123)
   Authenticated user found: username (your@email.com)
   Company profile found: Your Company Name
   Has logo: True
   Has contact info: True
   Profile complete: True
   Applying brand overlay...
   Brand overlay applied successfully!
   ```

## Requirements

For branding to work, your company profile must have:
- ✅ **Company Name** (required)
- ✅ **WhatsApp Number** (required)
- ✅ **Logo** (optional but recommended)
- ✅ **Email or Facebook** (optional)

## If Still Not Working

### Check 1: Verify Headers Are Sent
Open browser console and look for:
```
📧 Sending Clerk email to backend: your@email.com
```

If you don't see this, the Clerk user might not be loaded. Make sure you're signed in.

### Check 2: Verify User Found
Check backend logs for:
```
✅ Found user by Clerk email: your@email.com
```

If you see:
```
⚠️ No user found with Clerk email: your@email.com
```

This means the user doesn't exist in the backend. The backend will auto-create it, but you'll need to set up your company profile again.

### Check 3: Verify Company Profile
Check backend logs for:
```
Company profile found: Your Company Name
Profile complete: True
```

If you see:
```
No company profile found for user
```
or
```
Profile complete: False
```

Go to Settings → Company Profile and make sure:
- Company Name is filled
- WhatsApp Number is filled

### Check 4: User Mismatch
If the backend finds a different user than expected:
- The email in Clerk might not match the email in Django
- Check backend logs to see which user was found
- Make sure you're signed in with the correct account

## Files Modified

1. `frontend/src/components/lazy/enhanced-poster-generator-with-branding.tsx`
   - Added Clerk user headers (X-CLERK-EMAIL, X-CLERK-ID, etc.)
   - Added console logging for debugging

2. `backend/ai_services/ai_poster_views.py`
   - Improved user lookup to prioritize Clerk email
   - Better logging for debugging

## Expected Result

After this fix:
- ✅ Backend correctly identifies you by email
- ✅ Backend finds your company profile
- ✅ Branding is applied to generated posters
- ✅ Posters include your logo and contact information

## Debugging Commands

### Check Your Company Profile (Browser Console)
```javascript
fetch('/api/company-profiles/')
  .then(r => r.json())
  .then(profile => {
    console.log('Company Name:', profile.company_name);
    console.log('WhatsApp:', profile.whatsapp_number);
    console.log('Has Logo:', !!profile.logo);
    console.log('Has Complete Profile:', profile.has_complete_profile);
  });
```

### Check Backend User (Backend Logs)
Look for these log messages when generating a poster:
- `✅ Found user by Clerk email: ...`
- `Company profile found: ...`
- `Profile complete: True/False`
- `Applying brand overlay...`

