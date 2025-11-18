# Clerk Google OAuth Setup Guide

## Overview

This guide will help you set up Google OAuth authentication with Clerk for the Frameio application.

## Prerequisites

- A Clerk account (free tier available at https://clerk.com)
- A Google Cloud Console account for OAuth configuration

## Step 1: Create a Clerk Application

1. Go to https://clerk.com and sign up or log in
2. Create a new application or select an existing one
3. Navigate to your application dashboard

## Step 2: Enable Google OAuth in Clerk

1. In your Clerk dashboard, go to **User & Authentication** → **Social Connections**
2. Find **Google** in the list of OAuth providers
3. Click **Enable** on Google
4. You'll see two options:
   - **Use Clerk's development keys** (for testing only)
   - **Use custom credentials** (for production)

### Option A: Development (Quick Setup)

For development and testing:
1. Toggle **Use Clerk's development keys**
2. Save the settings
3. Google OAuth is now enabled with Clerk's test credentials

⚠️ **Note**: Development keys are rate-limited and should only be used for testing.

### Option B: Production (Custom Credentials)

For production deployment:

#### 2.1: Create Google OAuth Credentials

1. Go to https://console.cloud.google.com
2. Create a new project or select an existing one
3. Navigate to **APIs & Services** → **Credentials**
4. Click **Create Credentials** → **OAuth 2.0 Client ID**
5. Configure the OAuth consent screen if prompted:
   - App name: Frameio
   - User support email: your email
   - Developer contact: your email
6. For **Application type**, select **Web application**
7. Add **Authorized JavaScript origins**:
   ```
   http://localhost:3000
   https://yourdomain.com (for production)
   ```
8. Add **Authorized redirect URIs**:
   ```
   https://your-clerk-subdomain.clerk.accounts.dev/v1/oauth_callback
   ```
   (You'll find your exact redirect URI in Clerk's Google settings)
9. Click **Create**
10. Copy your **Client ID** and **Client Secret**

#### 2.2: Configure Custom Credentials in Clerk

1. Return to Clerk dashboard → **Social Connections** → **Google**
2. Toggle **Use custom credentials**
3. Paste your **Client ID** and **Client Secret**
4. Save the settings

## Step 3: Configure Environment Variables

### Frontend (.env.local in frontend directory)

Create or update `frontend/.env.local`:

```bash
# Clerk Configuration
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Optional: If using custom Clerk domain
NEXT_PUBLIC_CLERK_FRONTEND_API=https://your-clerk-subdomain.clerk.accounts.dev
```

### Backend (.env in root directory)

Update the root `.env` file:

```bash
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
CLERK_SECRET_KEY=sk_test_your_secret_key_here
NEXT_PUBLIC_CLERK_FRONTEND_API=https://your-clerk-subdomain.clerk.accounts.dev
```

## Step 4: Get Your Clerk Keys

1. In Clerk dashboard, go to **API Keys**
2. Copy your **Publishable Key** (starts with `pk_test_` or `pk_live_`)
3. Copy your **Secret Key** (starts with `sk_test_` or `sk_live_`)
4. Your **Frontend API** URL is visible at the top (format: `https://[subdomain].clerk.accounts.dev`)

## Step 5: Update Allowed Origins and Redirect URLs in Clerk

1. In Clerk dashboard, go to **Paths**
2. Ensure these URLs are configured:
   - **Sign-in URL**: `/sign-in`
   - **Sign-up URL**: `/sign-up`
   - **Home URL**: `/`
   - **After sign-in URL**: `/dashboard`
   - **After sign-up URL**: `/dashboard`

3. Go to **Domain & URLs**
4. Add your development and production URLs:
   - Development: `http://localhost:3000`
   - Production: `https://yourdomain.com`

## Step 6: Test the Authentication Flow

1. Start your backend server:
   ```bash
   cd backend
   python manage.py runserver
   ```

2. Start your frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```

3. Navigate to http://localhost:3000/sign-up

4. You should see the Clerk sign-up form with:
   - Email/password fields
   - **Continue with Google** button
   - Other OAuth providers (if enabled)

5. Click **Continue with Google**:
   - You'll be redirected to Google's OAuth consent screen
   - Grant permissions
   - You'll be redirected back to your app and signed in
   - Should redirect to `/dashboard`

## Troubleshooting

### Error: "Unable to complete action at this time"

**Causes:**
1. Missing or invalid Clerk environment variables
2. Incorrect redirect URIs in Google Console
3. OAuth consent screen not properly configured
4. Google OAuth not enabled in Clerk dashboard

**Solutions:**
1. Verify all environment variables are set correctly
2. Restart your development server after changing .env files
3. Check Clerk logs in dashboard → **Logs** for detailed error messages
4. Ensure redirect URIs match exactly (including https/http)
5. Clear browser cookies and cache
6. Check that Google OAuth is enabled in Clerk dashboard

### Error: "Redirect URI mismatch"

1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client
3. Verify the authorized redirect URI matches exactly what Clerk provides
4. Common format: `https://[your-subdomain].clerk.accounts.dev/v1/oauth_callback`

### Error: "Invalid publishable key"

1. Ensure you're using the correct key for your environment (test vs live)
2. Check for extra spaces or line breaks in .env file
3. Verify the key starts with `pk_test_` or `pk_live_`
4. Regenerate keys in Clerk dashboard if needed

### Google OAuth button not showing

1. Verify Google is enabled in Clerk dashboard
2. Check browser console for errors
3. Ensure Clerk components are properly imported
4. Verify `ClerkProvider` wraps your application in `layout.tsx`

## Security Best Practices

1. **Never commit secrets**: Add `.env` and `.env.local` to `.gitignore`
2. **Use different keys for environments**: Separate test/live keys for dev/prod
3. **Rotate keys regularly**: Especially after any security incident
4. **Enable 2FA**: On your Clerk and Google Cloud accounts
5. **Monitor logs**: Check Clerk dashboard logs regularly for suspicious activity
6. **Restrict OAuth scopes**: Only request necessary Google permissions

## Production Deployment Checklist

- [ ] Use custom Google OAuth credentials (not Clerk's dev keys)
- [ ] Switch to live Clerk keys (`pk_live_*` and `sk_live_*`)
- [ ] Update authorized origins in Google Console with production domain
- [ ] Update redirect URIs in Google Console with production Clerk URLs
- [ ] Set proper CORS settings in backend
- [ ] Enable HTTPS on production domain
- [ ] Test complete OAuth flow on production
- [ ] Set up error monitoring (Sentry, etc.)
- [ ] Review and publish Google OAuth consent screen
- [ ] Add privacy policy and terms of service URLs

## Additional OAuth Providers

To enable more OAuth providers (GitHub, Facebook, Microsoft, etc.):

1. Go to Clerk dashboard → **Social Connections**
2. Enable desired providers
3. Configure custom credentials (similar to Google)
4. They'll automatically appear on your sign-in/sign-up forms

## Support

- **Clerk Documentation**: https://clerk.com/docs
- **Clerk Discord**: https://discord.com/invite/b5rXHjAg7A
- **Google OAuth Guide**: https://developers.google.com/identity/protocols/oauth2

## Summary

You've now configured Google OAuth authentication with Clerk! Users can:
- Sign up with Google (one-click)
- Sign in with Google
- Link Google to existing accounts
- Manage their authentication methods in account settings

The authentication flow is fully managed by Clerk, providing enterprise-grade security without the complexity.

