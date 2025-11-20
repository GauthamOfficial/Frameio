# API Key Issue - Supervisor Checklist

## Problem
The API key `AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps` is returning "API key expired" error, but it works on another developer's system.

## Error Message
```
400 INVALID_ARGUMENT. API key expired. Please renew the API key.
Reason: API_KEY_INVALID
```

## Required Actions (Please Check)

### 1. Verify API Key Status
**Location:** https://console.cloud.google.com/apis/credentials

- [ ] Open the API key in Google Cloud Console
- [ ] Verify status is "Active" (not "Disabled" or "Deleted")
- [ ] Check creation date and expiration (if any)
- [ ] Verify the key hasn't been rotated or regenerated

### 2. Check API Restrictions
**Location:** API Key → "API restrictions" section

- [ ] **If "Restrict key" is enabled:**
  - [ ] Ensure "Generative Language API" is in the allowed list
  - [ ] Add if missing: `generativelanguage.googleapis.com`

### 3. Check Application Restrictions
**Location:** API Key → "Application restrictions" section

**Most Common Issue:** IP address restrictions

- [ ] **If "IP addresses" is selected:**
  - [ ] Add the developer's IP address to allowed list
  - [ ] Or change to "None" for development (less secure but works everywhere)
  
- [ ] **If "HTTP referrers" is selected:**
  - [ ] Add `localhost:8000` and `127.0.0.1:8000` to allowed referrers
  - [ ] Or change to "None" for development

- [ ] **If "None" is selected:**
  - [ ] Key should work from anywhere (this is the most permissive setting)

### 4. Verify API is Enabled
**Location:** https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com

- [ ] Ensure "Generative Language API" is **ENABLED** for the project
- [ ] If disabled, click "Enable"

### 5. Check Billing
**Location:** https://console.cloud.google.com/billing

- [ ] Verify billing account is linked to the project
- [ ] Some APIs require billing even for free tier

### 6. Check Quotas
**Location:** https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas

- [ ] Verify quotas haven't been exceeded
- [ ] Check if there are any rate limits being hit

## Quick Fix Options

### Option 1: Remove IP Restrictions (Recommended for Development)
1. Go to API key settings
2. Under "Application restrictions", select "None"
3. Save changes
4. Wait 1-2 minutes for changes to propagate

### Option 2: Add Developer's IP Address
1. Get developer's IP: Ask them to visit https://whatismyipaddress.com
2. Go to API key settings
3. Under "Application restrictions" → "IP addresses"
4. Add the IP address
5. Save changes

### Option 3: Enable API (If Disabled)
1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click "Enable"
3. Wait for activation

## Why It Works on Friend's System But Not This One

**Most Likely Causes:**
1. **IP Address Restriction:** Friend's IP is in allowed list, this developer's is not
2. **Network Location:** Friend might be on a different network (office vs home)
3. **API Restrictions:** Friend's system might be using a different API key
4. **Cached Credentials:** Friend's system might have cached valid credentials

## Testing After Changes

After making changes, the developer should:
1. Wait 1-2 minutes for changes to propagate
2. Restart the backend server
3. Run: `python backend/diagnose_api_key_issue.py`
4. Try generating a poster again

## Contact Information

If issues persist after checking all items above:
- Check Google Cloud Console logs
- Review API usage metrics
- Contact Google Cloud Support if needed

---

**Note:** API key changes can take 1-2 minutes to propagate. Please wait before testing again.








