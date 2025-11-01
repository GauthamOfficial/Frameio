# 🔑 Fix Leaked Gemini API Key

Your Gemini API key has been reported as leaked. Follow these steps to fix it:

## Step 1: Get a New Gemini API Key

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/app/apikey
   - Sign in with your Google account

2. **Create a New API Key:**
   - Click "Create API Key" or "Get API Key"
   - Select or create a Google Cloud project
   - Copy your new API key (starts with `AIza...`)

3. **Important:** 
   - Delete the old/leaked API key from your Google Cloud Console
   - Keep your new API key secure - don't share it publicly

## Step 2: Update Your Backend Configuration

You have two options:

### Option A: Use the Setup Script (Recommended)

```bash
# Navigate to backend directory
cd backend

# Run the setup script
python setup_gemini_env.py
```

The script will:
- Check if `.env` file exists (creates it if needed)
- Ask if you want to update the existing key
- Prompt you to enter your new API key
- Automatically update the `.env` file

### Option B: Manual Update

1. **Find or create `.env` file:**
   - Location: Root directory of your project (same level as `backend/` and `frontend/`)
   - If it doesn't exist, copy from template:
     ```bash
     cp env.template .env
     ```

2. **Edit the `.env` file:**
   - Open `.env` in a text editor
   - Find the line: `GEMINI_API_KEY=your_gemini_api_key_here`
   - Replace with: `GEMINI_API_KEY=AIzaSy...your_new_key_here`
   - Save the file

   **Example:**
   ```env
   GEMINI_API_KEY=AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps
   ```

## Step 3: Restart Your Backend Server

After updating the API key, **restart your Django backend server:**

```bash
# Stop the current server (Ctrl+C if running)

# Navigate to backend directory
cd backend

# Restart the server
python manage.py runserver
```

## Step 4: Verify It Works

1. **Check backend logs:**
   - Look for: `INFO: GEMINI_API_KEY configured`
   - Should NOT see: `WARNING: GEMINI_API_KEY not configured`

2. **Test in frontend:**
   - Try generating a poster again
   - The error should be gone

3. **Optional - Run test script:**
   ```bash
   cd backend
   python test_gemini_api.py
   ```

## Troubleshooting

### If you still see errors:

1. **Verify `.env` file location:**
   - Make sure `.env` is in the project root (same level as `backend/`)
   - Django loads it from there (see `settings.py`)

2. **Check environment variable:**
   ```bash
   # In backend directory
   python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('API Key:', os.getenv('GEMINI_API_KEY')[:20] + '...' if os.getenv('GEMINI_API_KEY') else 'NOT FOUND')"
   ```

3. **Restart the backend server:**
   - Environment variables are loaded on server start
   - Changes to `.env` require a server restart

### If you get a new error:

- **"Invalid API key"**: Double-check you copied the full key correctly
- **"Quota exceeded"**: You may have hit rate limits, wait a bit and try again
- **"Permission denied"**: The new key might need some time to activate (wait 1-2 minutes)

## Security Best Practices

1. **Never commit `.env` to git:**
   - Check that `.env` is in `.gitignore`
   
2. **Use different keys for dev/prod:**
   - Development and production should use separate API keys

3. **Rotate keys regularly:**
   - Set a reminder to rotate API keys every 3-6 months

4. **Monitor usage:**
   - Check Google Cloud Console for unexpected usage

## Need More Help?

- Google AI Studio: https://aistudio.google.com/app/apikey
- Project Documentation: See `README.md` and `SECURITY_BEST_PRACTICES.md`

