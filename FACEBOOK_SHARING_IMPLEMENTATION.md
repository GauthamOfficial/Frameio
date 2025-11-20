# Facebook Sharing Implementation Guide

This document describes the complete Facebook sharing workflow for the Framio project, including setup, testing, and troubleshooting.

## Overview

The Facebook sharing implementation provides:
- **Facebook Share Dialog** integration (client-side, no API required)
- **Open Graph (OG) meta tags** for rich link previews
- **Server-side rendering** of OG tags for Facebook crawler
- **Optional server-side Graph API** endpoint for future Page posting
- **Support for public and signed URLs** (S3 compatible)

## Architecture

### Frontend (Next.js App Router)
- **Route**: `app/poster/[id]/page.tsx` - Server component with OG meta tags
- **Component**: `components/poster/ShareButtons.tsx` - Facebook Share Dialog button
- **Helpers**: `lib/ogHelpers.ts` - OG tag generation utilities

### Backend (Django REST Framework)
- **Endpoint**: `GET /api/ai/posters/{id}/share/` - Returns optimized share data
- **Storage**: `ai_services/utils/storage.py` - Handles public/signed URLs
- **Serializer**: `PosterShareSerializer` - Validates share data
- **Optional**: `POST /api/ai/social/facebook/post/` - Graph API posting (future)

## Setup Instructions

### 1. Environment Variables

Add to your `.env` file:

```bash
# Frontend
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Backend (optional, for S3 signed URLs)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_STORAGE_BUCKET_NAME=your_bucket_name
AWS_S3_REGION_NAME=us-east-1

# Facebook Graph API (optional, for server-side posting)
FB_PAGE_ACCESS_TOKEN=your_page_access_token
```

### 2. Local Development with Tunnel

#### Option A: Cloudflare Tunnel (Recommended - No Auth Required)

**Step 1: Start Cloudflare Tunnel**
```bash
# Automatic (downloads and starts)
node start-cloudflare-tunnel.js

# OR manual
cloudflared tunnel --url http://localhost:3000
```

**Step 2: Copy the public URL**
The tunnel will display a URL like: `https://abc123.trycloudflare.com`

**Step 3: Update environment variables**
```bash
# In frontend/.env.local
NEXT_PUBLIC_APP_URL=https://abc123.trycloudflare.com
```

#### Option B: ngrok (Requires Account)

**Step 1: Sign up and configure**
```bash
# Sign up at https://dashboard.ngrok.com/signup
# Get your authtoken from https://dashboard.ngrok.com/get-started/your-authtoken
ngrok config add-authtoken YOUR_AUTHTOKEN_HERE
```

**Step 2: Start ngrok**
```bash
ngrok http 3000
```

**Step 3: Update environment variables**
Copy the ngrok HTTPS URL and set:
```bash
NEXT_PUBLIC_APP_URL=https://abc123.ngrok.io
```

#### Step 4: Start your services
```bash
# Terminal 1: Start Django backend
cd backend
python manage.py runserver

# Terminal 2: Start Next.js frontend
cd frontend
npm run dev

# Terminal 3: Start tunnel (Cloudflare or ngrok)
node start-cloudflare-tunnel.js
# OR: ngrok http 3000
```

### 3. Testing Facebook Sharing

#### Step 1: Generate a poster
1. Navigate to the poster generator
2. Generate a poster with caption and hashtags
3. Note the poster ID from the URL or response

#### Step 2: Visit the poster page
```
https://your-ngrok-url.ngrok.io/poster/{poster-id}
```

#### Step 3: Verify OG tags
View page source and check for:
```html
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:image" content="...">
<meta property="og:url" content="...">
<meta property="og:type" content="article">
<meta property="og:image:width" content="1080">
<meta property="og:image:height" content="1350">
```

#### Step 4: Test with Facebook Sharing Debugger
1. Visit: https://developers.facebook.com/tools/debug/
2. Paste your poster URL: `https://your-ngrok-url.ngrok.io/poster/{poster-id}`
3. Click "Debug"
4. Verify:
   - ✅ Title shows correctly (max 60 chars)
   - ✅ Description shows correctly (max 200 chars)
   - ✅ Image preview displays
   - ✅ No errors or warnings

#### Step 5: Test Share Dialog
1. Click "Share on Facebook" button on the poster page
2. Facebook Share Dialog should open in popup
3. Verify preview shows correct image, title, and description

## API Endpoints

### GET /api/ai/posters/{id}/share/

Returns optimized poster data for social media sharing.

**Response:**
```json
{
  "id": "uuid",
  "caption": "Poster caption",
  "hashtags": ["#tag1", "#tag2"],
  "image_url": "https://absolute-url-to-image.jpg",
  "image_width": 1080,
  "image_height": 1350,
  "created_at": "2024-01-01T00:00:00Z",
  "og_title": "Optimized title (max 60 chars)",
  "og_description": "Optimized description (max 200 chars)"
}
```

**Features:**
- Returns absolute image URLs (converts relative to absolute)
- Generates signed URLs for private S3 images (TTL: 600s)
- Optimizes OG title and description
- Caches responses for 10 minutes

### POST /api/ai/social/facebook/post/ (Optional)

Post a poster to a Facebook Page using Graph API.

**Request:**
```json
{
  "poster_id": "uuid",
  "page_id": "facebook_page_id",
  "message": "Custom message (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "post_id": "facebook_post_id",
  "url": "https://facebook.com/...",
  "message": "Post published successfully"
}
```

**Requirements:**
- User must be authenticated
- User must own the poster or be admin
- `FB_PAGE_ACCESS_TOKEN` must be configured

## Testing Checklist

### ✅ Basic Functionality
- [ ] Poster page loads with correct OG tags
- [ ] Image URL is absolute and accessible
- [ ] OG title is truncated to max 60 chars
- [ ] OG description is truncated to max 200 chars
- [ ] Share button opens Facebook Share Dialog

### ✅ Facebook Sharing Debugger
- [ ] URL passes Facebook Sharing Debugger
- [ ] Image preview displays correctly
- [ ] Title and description show correctly
- [ ] No errors or warnings

### ✅ Edge Cases
- [ ] Poster with no hashtags
- [ ] Poster with null dimensions
- [ ] Very long caption (truncation works)
- [ ] Relative image URL (converted to absolute)
- [ ] Private S3 image (signed URL generated)

### ✅ Performance
- [ ] Share endpoint response cached (check Redis)
- [ ] OG tags render server-side (view page source)
- [ ] No client-side errors in console

## Troubleshooting

### Issue: OG image doesn't show in Facebook preview

**Solutions:**
1. **Check image URL is absolute:**
   ```bash
   curl -I https://your-image-url.jpg
   # Should return 200 OK
   ```

2. **Verify image is publicly accessible:**
   - For local dev: Ensure Django serves media files
   - For S3: Check bucket policy allows public read

3. **Check image dimensions:**
   - Minimum: 200x200 pixels
   - Recommended: 1200x630 pixels (1.91:1 ratio)

4. **Force Facebook to re-scrape:**
   - Use Sharing Debugger: https://developers.facebook.com/tools/debug/
   - Click "Scrape Again"

### Issue: Share Dialog shows wrong preview

**Solutions:**
1. Clear Facebook's cache using Sharing Debugger
2. Verify OG tags in page source
3. Ensure `og:url` matches the actual page URL
4. Check that image URL is accessible from Facebook's servers

### Issue: Signed URLs expire too quickly

**Solution:**
Increase TTL in `backend/ai_services/ai_poster_views.py`:
```python
signed_url = get_signed_image_url(image_url, expiration=3600, request=request)  # 1 hour
```

### Issue: ngrok URL changes on restart

**Solution:**
1. Use ngrok's static domain (paid plan)
2. Or update `NEXT_PUBLIC_APP_URL` after each restart
3. Or use Cloudflare Tunnel (free, more stable)

## cURL Commands for Testing

### Test share endpoint:
```bash
curl -X GET "http://localhost:8000/api/ai/posters/{poster-id}/share/" \
  -H "Content-Type: application/json"
```

### Test poster page:
```bash
curl -I "https://your-ngrok-url.ngrok.io/poster/{poster-id}"
```

### Test Facebook Graph API (optional):
```bash
curl -X GET "https://graph.facebook.com/?id=https://your-ngrok-url.ngrok.io/poster/{poster-id}" \
  -H "Content-Type: application/json"
```

## Code Examples

### Next.js Server Component OG Meta Example

```typescript
export async function generateMetadata({ params }: PosterPageProps): Promise<Metadata> {
  const shareData = await getPosterShareData(params.id)
  
  return {
    title: shareData.og_title,
    description: shareData.og_description,
    openGraph: {
      type: 'article',
      title: shareData.og_title,
      description: shareData.og_description,
      url: buildPosterPageUrl(params.id),
      images: [{
        url: ensureAbsoluteUrl(shareData.image_url),
        width: shareData.image_width || 1200,
        height: shareData.image_height || 630,
      }],
    },
  }
}
```

### Django PosterShareSerializer Snippet

```python
class PosterShareSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    caption = serializers.CharField()
    hashtags = serializers.ListField(child=serializers.CharField())
    image_url = serializers.URLField()
    image_width = serializers.IntegerField(required=False, allow_null=True)
    image_height = serializers.IntegerField(required=False, allow_null=True)
    created_at = serializers.DateTimeField()
    og_title = serializers.CharField(required=False)
    og_description = serializers.CharField(required=False)
```

### ngrok Testing Commands

```bash
# Start ngrok
ngrok http 3000

# Check ngrok status
curl http://localhost:4040/api/tunnels

# Get ngrok URL programmatically
curl http://localhost:4040/api/tunnels | jq '.tunnels[0].public_url'
```

## Security Considerations

1. **Do NOT expose PII in OG tags** - Only use public poster data
2. **Signed URLs** - Keep TTL short (600s default) and rotate keys regularly
3. **Facebook Page Tokens** - Store encrypted in database, never in frontend
4. **Rate Limiting** - Share endpoint is cached to prevent abuse
5. **CORS** - Ensure proper CORS headers for image access

## Future Enhancements

- [ ] Facebook OAuth integration for Page access tokens
- [ ] Multiple Facebook Pages support
- [ ] Scheduled Facebook posts
- [ ] Analytics for shared posts
- [ ] A/B testing for OG tag optimization

## Support

For issues or questions:
1. Check Facebook Sharing Debugger for errors
2. Review server logs for backend errors
3. Check browser console for frontend errors
4. Verify environment variables are set correctly

## References

- [Facebook Share Dialog](https://developers.facebook.com/docs/sharing/web)
- [Open Graph Protocol](https://ogp.me/)
- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [Next.js Metadata API](https://nextjs.org/docs/app/api-reference/functions/generate-metadata)

