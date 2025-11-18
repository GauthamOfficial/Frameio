# Quick Start: Fix Clerk Google OAuth

## The Problem
You're seeing: **"Unable to complete action at this time. If the problem persists please contact support."**

This is because Google OAuth isn't set up yet. Follow these steps to fix it:

---

## Step 1: Create Clerk Account (5 minutes)

1. Go to https://clerk.com and sign up (it's free)
2. Click **"Create Application"**
3. Give it a name (e.g., "Frameio")
4. Click **Create**

---

## Step 2: Enable Google OAuth (2 minutes)

1. In your Clerk dashboard, click **"User & Authentication"** in sidebar
2. Click **"Social Connections"**
3. Find **Google** in the list
4. Click **Enable**
5. Toggle **"Use Clerk's development keys"** (for testing)
6. Click **Save**

✅ Google OAuth is now enabled!

---

## Step 3: Get Your Clerk Keys (1 minute)

1. In Clerk dashboard, click **"API Keys"** in sidebar
2. Copy these three values:
   - **Publishable Key** (starts with `pk_test_`)
   - **Secret Key** (starts with `sk_test_`) - click "Show" first
   - **Frontend API** (at the top, looks like `https://[something].clerk.accounts.dev`)

---

## Step 4: Configure Environment Variables (3 minutes)

### A. Root `.env` file

Open your root `.env` file and add/update these lines:

```bash
CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE
NEXT_PUBLIC_CLERK_FRONTEND_API=https://YOUR_SUBDOMAIN.clerk.accounts.dev
```

### B. Frontend `.env.local` file

Create `frontend/.env.local` (if it doesn't exist):

```bash
# Copy the template
cp frontend/env.local.template frontend/.env.local
```

Then open `frontend/.env.local` and update:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE
NEXT_PUBLIC_CLERK_FRONTEND_API=https://YOUR_SUBDOMAIN.clerk.accounts.dev

# These should already be there
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

---

## Step 5: Verify Configuration (1 minute)

Run this command to check if everything is set up correctly:

```bash
node test-clerk-oauth.js
```

✅ If you see "All Clerk environment variables are configured!" - you're good!  
❌ If you see errors, fix the missing values and run again.

---

## Step 6: Restart Your Servers (1 minute)

### Stop any running servers (Ctrl+C), then:

#### Backend:
```bash
cd backend
python manage.py runserver
```

#### Frontend (new terminal):
```bash
cd frontend
npm run dev
```

---

## Step 7: Test It! (1 minute)

1. Open http://localhost:3000/sign-up
2. You should see:
   - ✅ Email/password fields
   - ✅ **"Continue with Google"** button
   - ✅ Professional Clerk UI

3. Click **"Continue with Google"**:
   - Should redirect to Google
   - Choose your Google account
   - Should redirect back and log you in
   - Should land on the dashboard

🎉 **Google OAuth is working!**

---

## Troubleshooting

### "Continue with Google" button not showing?

1. Make sure Google is **enabled** in Clerk dashboard → Social Connections
2. Restart your frontend server (`npm run dev`)
3. Clear browser cache and reload

### Still seeing the error message?

1. Run `node test-clerk-oauth.js` to verify configuration
2. Check Clerk dashboard → **Logs** for detailed errors
3. Make sure you restarted BOTH servers after updating .env
4. Check browser console (F12) for error messages

### "Redirect URI mismatch" error?

1. In Clerk dashboard, go to **Paths**
2. Make sure these are set:
   - Sign-in URL: `/sign-in`
   - Sign-up URL: `/sign-up`
   - After sign-in: `/dashboard`

---

## What Changed?

The code has been updated to use **Clerk's built-in authentication** instead of the custom auth system. This gives you:

- ✅ Google OAuth (one-click signup)
- ✅ Email/password authentication
- ✅ Professional UI
- ✅ Secure session management
- ✅ Easy to add more OAuth providers (GitHub, Facebook, etc.)

---

## Need More Help?

- **Detailed Setup Guide**: See [CLERK_GOOGLE_OAUTH_SETUP.md](CLERK_GOOGLE_OAUTH_SETUP.md)
- **Fix Summary**: See [CLERK_AUTH_FIX_SUMMARY.md](CLERK_AUTH_FIX_SUMMARY.md)
- **Clerk Docs**: https://clerk.com/docs
- **Clerk Support**: https://discord.com/invite/b5rXHjAg7A

---

## For Production

When you're ready to deploy:

1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials
3. Add them to Clerk (instead of using dev keys)
4. Switch to Clerk's live keys (`pk_live_*` and `sk_live_*`)
5. See [CLERK_GOOGLE_OAUTH_SETUP.md](CLERK_GOOGLE_OAUTH_SETUP.md) for details

---

**Total Time: ~15 minutes** ⏱️

