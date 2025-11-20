# Branding Kit Dashboard Debugging Guide

## Issue: Generated branding kits not showing on dashboard

### Step 1: Check Database Migration

First, ensure the database table exists:

```bash
cd backend
python manage.py makemigrations ai_services
python manage.py migrate
```

### Step 2: Test Database Contents

Run the test script to see if branding kits are in the database:

```bash
cd backend
python test_branding_kit.py
```

This will show:
- If the table exists
- How many branding kits are in the database
- Details of recent branding kits
- User associations

### Step 3: Check Backend Logs

When you generate a branding kit, check the backend console for these log messages:

**During Generation:**
- `Request user: ...` - Should show the authenticated user
- `Authenticated user: ...` - Should show user email
- `Branding kit saved to database with ID: ...` - Confirms save was successful

**When Fetching History:**
- `List branding kits - Request user: ...` - Should show authenticated user
- `List branding kits - Total branding kits in DB: X` - Total count in database
- `List branding kits - Filtered by user: X kits` - How many match the user
- `List branding kits - Returning X kits` - What's being returned

### Step 4: Check Frontend Console

Open browser DevTools (F12) and check the Console tab:

**When Generating:**
- Look for any errors in the Network tab
- Check if the Authorization header is being sent

**When Loading Dashboard:**
- `Fetching branding kits from: ...` - Should show the correct URL
- `Response status: 200` - Should be successful
- `Branding kits response data: ...` - Should show the API response
- `Setting X branding kits` - Should show how many are being set

### Step 5: Common Issues and Fixes

#### Issue 1: "Table doesn't exist" error
**Solution:** Run migrations
```bash
cd backend
python manage.py migrate
```

#### Issue 2: No authenticated user in logs
**Solution:** 
- Check if the frontend is sending the Authorization header
- Verify the token is valid
- Check browser Network tab to see if `Authorization: Bearer <token>` is in request headers

#### Issue 3: Branding kits saved but not showing
**Possible causes:**
- User mismatch: Kit saved with one user, fetched with another
- Organization mismatch: Kit saved to organization A, user belongs to organization B
- Authentication issue: User not authenticated when fetching

**Check:**
```bash
# Run the test script to see user associations
python test_branding_kit.py
```

#### Issue 4: Empty response from API
**Check:**
- Backend logs should show filtering details
- If DEBUG mode, it should show all kits even without auth
- If PRODUCTION mode, it requires authentication

### Step 6: Manual API Test

Test the API endpoint directly:

```bash
# Get your auth token from browser localStorage or from the app
TOKEN="your_token_here"

# Test the history endpoint
curl -X GET "http://localhost:8000/api/ai/branding-kit/history/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"
```

Or use the browser:
1. Open DevTools > Network tab
2. Navigate to dashboard
3. Find the request to `/api/ai/branding-kit/history/`
4. Check the Response tab

### Step 7: Verify Data Structure

The API should return:
```json
{
  "success": true,
  "results": [
    {
      "id": "...",
      "prompt": "...",
      "style": "modern",
      "logo": {
        "data": "base64...",
        "format": "png"
      },
      "color_palette": {
        "data": "base64...",
        "format": "png"
      },
      "colors": ["#hex1", "#hex2"],
      "created_at": "2024-...",
      "updated_at": "2024-..."
    }
  ],
  "count": 1,
  "limit": 50,
  "offset": 0
}
```

### Quick Fixes

1. **If migration not run:**
   ```bash
   cd backend
   python manage.py makemigrations ai_services
   python manage.py migrate
   ```

2. **If authentication not working:**
   - Check browser Network tab for Authorization header
   - Verify token in localStorage: `localStorage.getItem('auth-token')`
   - Check backend authentication logs

3. **If data not saving:**
   - Check backend logs for "Failed to save branding kit"
   - Verify database connection
   - Check if logo_data/palette_data are too large (base64 can be very long)

4. **If showing wrong user's kits:**
   - Check user authentication
   - Verify organization membership
   - Check backend logs for filtering details

### Still Not Working?

1. Share the output of `python test_branding_kit.py`
2. Share relevant backend log lines (especially around generation and fetching)
3. Share browser console logs
4. Share the API response from Network tab

