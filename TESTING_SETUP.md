# Automated Testing Setup with Playwright

## Installation

```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

## Add Scripts to package.json

Add these to your `frontend/package.json`:

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:tunnel": "TUNNEL_URL=$TUNNEL_URL playwright test",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:report": "playwright show-report"
  }
}
```

## Running Tests

### Test Localhost

```bash
npm run test:e2e
```

### Test via Tunnel

1. **Start tunnel:**
   ```bash
   node start-cloudflare-tunnel.js
   ```

2. **Copy tunnel URL** (e.g., `https://abc-def-ghi.trycloudflare.com`)

3. **Run tests:**
   ```bash
   TUNNEL_URL=https://your-tunnel-url.trycloudflare.com npm run test:e2e
   ```

   Or on Windows PowerShell:
   ```powershell
   $env:TUNNEL_URL="https://your-tunnel-url.trycloudflare.com"; npm run test:e2e
   ```

### Interactive UI Mode

```bash
npm run test:e2e:ui
```

### Debug Mode

```bash
npm run test:e2e:debug
```

### View Test Report

```bash
npm run test:e2e:report
```

## Test Files Created

1. **`tests/tunnel-health.spec.ts`**
   - Checks tunnel is accessible
   - Verifies no ERR_BLOCKED_BY_CLIENT errors
   - Confirms API calls use relative paths via tunnel

2. **`tests/poster-generation.spec.ts`**
   - Tests poster generator loads
   - Verifies API connections work via tunnel
   - Checks for console errors

3. **`tests/facebook-sharing.spec.ts`**
   - Tests Facebook share button
   - Verifies public URL check
   - Validates Open Graph tags on poster pages

## Test Scenarios Covered

### ✅ Tunnel Health
- Dashboard loads without Cloudflare errors
- No `ERR_BLOCKED_BY_CLIENT` console errors
- API requests use relative paths (not `localhost:8000`)
- Stats load correctly
- Posters list loads

### ✅ Poster Generation
- Generator page loads
- No API connection errors
- Tunnel access detection works
- Forms are functional

### ✅ Facebook Sharing
- Share buttons present
- Public URL validation works
- Facebook Share Dialog opens with tunnel URL
- Open Graph meta tags rendered correctly

## Environment Variables

Create `.env.test` in frontend:

```bash
# Tunnel URL (set this when testing via tunnel)
TUNNEL_URL=https://your-tunnel-url.trycloudflare.com

# Optional: Test poster ID for OG tag testing
TEST_POSTER_ID=your-poster-uuid

# Skip starting web server (if you have it running)
SKIP_WEBSERVER=true
```

## CI/CD Integration

Add to your GitHub Actions workflow:

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Install Playwright
        run: |
          cd frontend
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
      
      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

## What Happens Next?

Once your tunnel is running, I can:

1. **Run these tests automatically** via browser automation
2. **Report results** with screenshots
3. **Identify issues** immediately
4. **Verify fixes** work correctly

## Start Testing Now

1. **Start tunnel:**
   ```bash
   node start-cloudflare-tunnel.js
   ```

2. **Get tunnel URL** (will be shown in console)

3. **Tell me the URL** and I'll run automated tests via browser automation

Or run them yourself:

```bash
TUNNEL_URL=https://your-url.trycloudflare.com npm run test:e2e
```

## Troubleshooting

### Tests fail with "net::ERR_CONNECTION_REFUSED"
- **Cause:** Frontend not running
- **Fix:** `npm run dev`

### Tests fail with "Cloudflare Tunnel error"
- **Cause:** Tunnel not running
- **Fix:** `node start-cloudflare-tunnel.js`

### Tests fail with "ERR_BLOCKED_BY_CLIENT"
- **Cause:** Code not updated or frontend not restarted
- **Fix:** Restart frontend to pick up code changes

### Tests timeout
- **Cause:** Backend not running
- **Fix:** `cd backend && python manage.py runserver`




