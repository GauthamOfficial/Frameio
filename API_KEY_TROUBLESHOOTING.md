# API Key Troubleshooting Guide

## Issue: "API key expired" error but key works on friend's system

### Quick Diagnosis

Run the diagnostic script:
```bash
cd backend
python diagnose_api_key_issue.py
```

### Common Causes & Solutions

#### 1. **API Restrictions (Most Likely)**
The API key might have restrictions that prevent it from working on your system.

**Check in Google Cloud Console:**
- Go to: https://console.cloud.google.com/apis/credentials
- Find your API key
- Check "API restrictions":
  - If restricted, ensure "Generative Language API" is enabled
- Check "Application restrictions":
  - **IP addresses**: Your IP might not be in the allowed list
  - **HTTP referrers**: Your localhost might not be allowed
  - **None**: Should work from anywhere

**Solution for Supervisor:**
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Click on the API key
3. Under "Application restrictions", either:
   - Set to "None" (for development)
   - Add your IP address to the allowed list
   - Add `localhost:8000` and `127.0.0.1:8000` to HTTP referrers

#### 2. **API Not Enabled**
The Generative Language API might not be enabled for the project.

**Check:**
- Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
- Ensure the API is enabled

**Solution for Supervisor:**
- Enable "Generative Language API" in the Google Cloud Console

#### 3. **Billing Not Enabled**
Some Google APIs require billing to be enabled.

**Check:**
- Go to: https://console.cloud.google.com/billing
- Verify billing is enabled for the project

#### 4. **Quota Exceeded**
The API key might have hit its quota limit.

**Check:**
- Go to: https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
- Check if quotas are exceeded

**Solution:**
- Wait for quota reset
- Request quota increase from supervisor

#### 5. **Key Status**
The key might be disabled or deleted.

**Check:**
- Go to: https://console.cloud.google.com/apis/credentials
- Verify the key status is "Active"

### Temporary Workaround

If the key works on your friend's system but not yours, try:

1. **Check your IP address:**
   ```bash
   curl ifconfig.me
   ```
   Ask supervisor to add this IP to allowed list

2. **Try from different network:**
   - Use mobile hotspot
   - Use different WiFi network
   - This helps identify if it's an IP restriction

3. **Check system time:**
   - Ensure your system clock is correct
   - API authentication can fail with incorrect time

4. **Verify network settings:**
   - Check firewall isn't blocking Google APIs
   - Check proxy settings
   - Try disabling VPN if active

### Information to Share with Supervisor

When asking for help, provide:

1. **Error message:** The exact error you're seeing
2. **Your IP address:** Run `curl ifconfig.me` or visit https://whatismyipaddress.com
3. **Diagnostic results:** Output from `diagnose_api_key_issue.py`
4. **System info:**
   - Operating system
   - Network type (home, office, VPN, etc.)
   - Any proxy or firewall settings

### Quick Fixes to Try

1. **Restart backend server:**
   ```bash
   # Stop server (Ctrl+C)
   cd backend
   python manage.py runserver
   ```

2. **Verify .env file:**
   ```bash
   cd backend
   cat .env | grep GEMINI_API_KEY
   ```

3. **Test API key directly:**
   ```bash
   cd backend
   python test_api_key.py
   ```

4. **Check for typos:**
   - Ensure no extra spaces in .env file
   - Ensure key is on single line
   - No quotes around the key value

### Expected .env Format

```env
GEMINI_API_KEY=AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps
```

**NOT:**
```env
GEMINI_API_KEY="AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps"  # No quotes
GEMINI_API_KEY = AIzaSyCdASB6S3egrc3tj7tRQ5ER6S7DgNzh2ps  # No spaces around =
```

### Still Not Working?

1. Run diagnostic: `python diagnose_api_key_issue.py`
2. Share results with supervisor
3. Ask supervisor to check:
   - API restrictions
   - API enablement
   - Billing status
   - Key status







