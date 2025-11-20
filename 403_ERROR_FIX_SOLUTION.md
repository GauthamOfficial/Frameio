# 🔧 Fix for 403/400 AxiosError - Gemini API Key Expired

## 🔍 Problem Identified

The error you're experiencing is caused by an **expired Gemini API key**. 

**Error Details:**
- Status Code: 400 INVALID_ARGUMENT (frontend may show as 403)
- Message: "API key expired. Please renew the API key."
- Current API Key: `AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps`

## ✅ Solution: Renew Your API Key

### Step 1: Create a New API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Create a New API Key:**
   - Click "Create API Key" or "Get API Key"
   - Select your Google Cloud project (or create a new one)
   - Copy the new API key

### Step 2: Update Your Environment Configuration

1. **Open the backend `.env` file:**
   ```
   D:\My Files\Yarl IT Hub\Framio\backend\.env
   ```

2. **Update the GEMINI_API_KEY line:**
   ```env
   GEMINI_API_KEY=YOUR_NEW_API_KEY_HERE
   ```
   Replace `YOUR_NEW_API_KEY_HERE` with the new key you just created

### Step 3: Restart the Backend Server

**Important:** You must restart your backend server for the changes to take effect.

```bash
# Stop the current server (Ctrl+C in the backend terminal)

# Then restart:
cd "D:\My Files\Yarl IT Hub\Framio\backend"
python manage.py runserver
```

Or use the batch file:
```bash
cd "D:\My Files\Yarl IT Hub\Framio"
start-backend.bat
```

### Step 4: Verify the Fix

After restarting, you can verify the API key is working:

```bash
cd "D:\My Files\Yarl IT Hub\Framio\backend"
python quick_api_test.py
```

You should see:
```
[OK] .env file loaded
[OK] API Key found: AIzaSy...
[OK] Google GenAI SDK imported successfully
[OK] Gemini client initialized
[OK] Text generation successful!
=== All Tests Passed! ===
```

## 🎯 Why This Happened

Google Gemini API keys can expire for several reasons:
- **Time-based expiration**: Keys may have an expiration date
- **Security policy**: Google may expire keys for security reasons
- **Account status changes**: Billing or project changes

## 🔐 Best Practices for API Keys

1. **Keep keys updated**: Check your API keys regularly
2. **Monitor usage**: Keep track of API quotas and limits
3. **Secure storage**: Never commit API keys to version control
4. **Environment-specific keys**: Use different keys for development and production
5. **Enable billing**: Some Gemini features require a billing account

## 📋 Additional Checks

If you still have issues after updating the API key:

### Check 1: Generative Language API Enabled
1. Go to: https://console.cloud.google.com/apis/library
2. Search for "Generative Language API"
3. Make sure it's enabled for your project

### Check 2: API Restrictions
1. Go to: https://console.cloud.google.com/apis/credentials
2. Click on your API key
3. Check "API restrictions" section
4. Ensure "Generative Language API" is allowed

### Check 3: Billing Enabled
1. Go to: https://console.cloud.google.com/billing
2. Make sure billing is enabled for your project
3. Some Gemini features require an active billing account

## 🆘 Still Having Issues?

If you're still experiencing errors after following these steps:

1. **Check the error message** in the browser console or backend logs
2. **Verify the API key** is correctly copied (no extra spaces)
3. **Check your Google Cloud project status**
4. **Try creating a new API key** from a different Google Cloud project

## 📞 Support Resources

- Google AI Studio: https://aistudio.google.com/
- Google Cloud Console: https://console.cloud.google.com/
- Gemini API Documentation: https://ai.google.dev/docs

---

**Current Status:** API key has been identified as expired. Follow the steps above to resolve the issue.



