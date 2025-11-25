# Dual-Mode Image Storage Implementation

This document describes the dual-mode image storage implementation for the poster generator, allowing seamless switching between Cloudinary (development) and local server storage (production) via environment variables.

## Overview

The implementation provides a unified storage handler that automatically routes image uploads to either Cloudinary or local file storage based on the `USE_CLOUDINARY` environment variable. This allows for:

- **Development (localhost)**: Use Cloudinary for easy testing and sharing
- **Production (VPS)**: Serve images directly from your own server without Cloudinary dependency

## Implementation Details

### 1. Environment Variables

Add the following to your `.env` file:

```bash
# Storage mode: True for Cloudinary, False for local storage
USE_CLOUDINARY=True  # Set to False for production on VPS

# Domain URL for local storage mode (required for production)
DOMAIN_URL=https://yourdomain.com  # Leave empty for localhost in development
```

### 2. Storage Handler

**File**: `backend/ai_services/utils/storage_handler.py`

The storage handler provides:
- `store_poster_image()`: Main function to store images in the configured mode
- `upload_poster_image()`: Upload existing images using the configured mode
- `create_and_store_shareable_page()`: Create and store HTML pages for Facebook sharing

**Modes**:
- **Cloudinary Mode** (`USE_CLOUDINARY=True`): Uploads to Cloudinary, returns secure URLs
- **Local Mode** (`USE_CLOUDINARY=False`): Saves to `MEDIA_ROOT/generated/`, returns local URLs

### 3. Settings Configuration

**File**: `backend/frameio_backend/settings.py`

Added settings:
```python
USE_CLOUDINARY = os.getenv('USE_CLOUDINARY', 'True').lower() == 'true'
DOMAIN_URL = os.getenv('DOMAIN_URL', '')
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### 4. Media File Serving

**Development**: Django automatically serves media files when `DEBUG=True` (configured in `urls.py`)

**Production**: Nginx serves media files directly (see `nginx.conf`)

**CORS Headers**: Media files are served with CORS headers to allow Facebook sharing:
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods: GET, HEAD, OPTIONS`
- `Access-Control-Allow-Headers: Content-Type`

### 5. API Response Format

The poster generation API returns:
```json
{
  "success": true,
  "image_url": "https://yourdomain.com/media/generated/poster_abc123.png",
  "caption": "Your generated caption text",
  "public_url": "https://yourdomain.com/media/generated/poster_abc123.png",
  // ... other fields
}
```

In Cloudinary mode, `public_url` will be a Cloudinary URL. In local mode, it will be your domain URL.

## Usage

### Development (Cloudinary Mode)

1. Set `USE_CLOUDINARY=True` in `.env`
2. Ensure Cloudinary credentials are set:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Run the server - images will be uploaded to Cloudinary

### Production (Local Storage Mode)

1. Set `USE_CLOUDINARY=False` in `.env`
2. Set `DOMAIN_URL=https://yourdomain.com` in `.env`
3. Configure Nginx (see `nginx.conf`)
4. Ensure `MEDIA_ROOT` directory exists and is writable
5. Run the server - images will be saved locally

## Nginx Configuration

The `nginx.conf` file includes:

1. **Media file serving** with CORS headers:
   ```nginx
   location /media/ {
       alias /opt/frameio/media/;
       add_header Access-Control-Allow-Origin "*" always;
       # ... other CORS headers
   }
   ```

2. **Proxy configuration** for Django:
   ```nginx
   location / {
       proxy_pass http://127.0.0.1:8000;
       # ... proxy headers
   }
   ```

**Important**: Update the paths in `nginx.conf` to match your server setup:
- `/opt/frameio/media/` → Your `MEDIA_ROOT` path
- `/opt/frameio/staticfiles/` → Your `STATIC_ROOT` path
- `your-domain.com` → Your actual domain

## File Structure

```
backend/
├── ai_services/
│   ├── utils/
│   │   ├── storage_handler.py      # Dual-mode storage handler
│   │   └── cloudinary_utils.py     # Cloudinary utilities (preserved)
│   ├── views/
│   │   └── media_views.py          # Media file serving with CORS
│   ├── ai_poster_service.py         # Updated to use storage handler
│   └── ai_poster_views.py          # API views (uses service)
├── frameio_backend/
│   ├── settings.py                  # Added USE_CLOUDINARY and DOMAIN_URL
│   └── urls.py                      # Media serving in development
└── media/
    └── generated/                   # Local storage directory
```

## Migration Guide

### Switching from Cloudinary to Local Storage

1. Set `USE_CLOUDINARY=False` in `.env`
2. Set `DOMAIN_URL=https://yourdomain.com` in `.env`
3. Configure Nginx (copy `nginx.conf` and update paths)
4. Restart Django server
5. New posters will be stored locally

**Note**: Existing Cloudinary URLs will continue to work. Only new posters will use local storage.

### Switching from Local to Cloudinary

1. Set `USE_CLOUDINARY=True` in `.env`
2. Ensure Cloudinary credentials are set
3. Restart Django server
4. New posters will be uploaded to Cloudinary

## Facebook Sharing

Both modes support Facebook sharing:

- **Cloudinary Mode**: Uses Cloudinary URLs (automatically public)
- **Local Mode**: Uses your domain URLs (must be publicly accessible)

**Requirements for Local Mode**:
- Images must be accessible via HTTPS
- CORS headers must be present (handled by Nginx)
- Domain must be publicly accessible (not localhost)

## Testing

### Test Cloudinary Mode
```bash
USE_CLOUDINARY=True python manage.py runserver
# Generate a poster - should upload to Cloudinary
```

### Test Local Mode
```bash
USE_CLOUDINARY=False DOMAIN_URL=http://localhost:8000 python manage.py runserver
# Generate a poster - should save locally
# Access at http://localhost:8000/media/generated/poster_*.png
```

## Troubleshooting

### Images not accessible in local mode
- Check that `MEDIA_ROOT` directory exists and is writable
- Verify `DOMAIN_URL` is set correctly
- Check Nginx configuration if in production
- Ensure CORS headers are present

### Cloudinary upload fails
- Verify Cloudinary credentials are set
- Check network connectivity
- Review Cloudinary dashboard for errors

### Facebook sharing doesn't work
- Ensure images are accessible via HTTPS (required by Facebook)
- Verify CORS headers are present
- Check that URLs are absolute (not relative)
- Test URL accessibility: `curl -I https://yourdomain.com/media/generated/poster.png`

## Security Considerations

1. **Local Storage**: Ensure `MEDIA_ROOT` has proper file permissions (readable by web server, writable by Django)
2. **CORS Headers**: Currently set to `*` for Facebook compatibility. Consider restricting in production if needed.
3. **File Access**: Media files are publicly accessible. Ensure sensitive files are not stored in `MEDIA_ROOT/generated/`.

## Future Enhancements

- Add file cleanup for old posters
- Implement CDN support for local storage
- Add image optimization before storage
- Support for multiple storage backends (S3, etc.)

