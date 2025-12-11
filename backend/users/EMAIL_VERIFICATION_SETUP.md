# Email Verification Setup

This document explains how email verification works in the Frameio application.

## Overview

The email verification system uses Django's built-in email backend with Gmail App Password authentication. When users register, they receive a verification email with a unique token that expires in 24 hours.

## Configuration

### 1. Gmail App Password Setup

1. Go to [Google Account Settings](https://myaccount.google.com/)
2. Navigate to **Security** → **2-Step Verification** (enable it if not already enabled)
3. Scroll down and click **App passwords**
4. Select **Mail** as the app and your device
5. Click **Generate**
6. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### 2. Environment Variables

Add these to your `.env` file:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_16_digit_app_password_here
EMAIL_TIMEOUT=10  # Connection timeout in seconds
DOMAIN_URL=http://localhost:8000  # For development
# DOMAIN_URL=https://yourdomain.com  # For production
```

**Note:** If `EMAIL_HOST_PASSWORD` is not set, emails will be printed to the console (development only).

## API Endpoints

### 1. Send Verification Email

**POST** `/api/users/auth/send-verification-email/`

Request body:
```json
{
  "email": "user@example.com"
}
```

Response:
```json
{
  "message": "Verification email sent successfully"
}
```

### 2. Verify Email

**GET/POST** `/api/users/auth/verify-email/{token}/`

Response:
```json
{
  "message": "Email verified successfully",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "is_verified": true
  }
}
```

### 3. Check Verification Status

**GET** `/api/users/auth/verification-status/`

Requires authentication.

Response:
```json
{
  "is_verified": true,
  "email": "user@example.com"
}
```

## User Registration Flow

1. User registers via `/api/users/auth/register/`
2. User account is created with `is_verified=False`
3. Verification email is automatically sent
4. User clicks link in email or uses the token to verify
5. User's `is_verified` field is set to `True`

## Database Models

### EmailVerificationToken

- `user`: Foreign key to User
- `token`: Unique verification token (32 characters)
- `is_used`: Boolean flag to prevent reuse
- `expires_at`: Expiration timestamp (24 hours from creation)
- `created_at`: Creation timestamp

Tokens are automatically cleaned up when used or expired.

## Email Templates

Verification emails include:
- Branded HTML template with gradient header
- Plain text fallback
- Verification button/link
- Expiration notice (24 hours)
- Security notice

## Testing

### Development Mode

If `EMAIL_HOST_PASSWORD` is not set, emails are printed to the console. Check your Django console output to see the email content.

### Production Mode

Ensure:
1. `EMAIL_HOST_PASSWORD` is set with a valid Gmail App Password
2. `DOMAIN_URL` is set to your production domain
3. Gmail account has 2-Step Verification enabled

## Troubleshooting

### Emails not sending / Connection timeout errors

**Error:** `[WinError 10060] A connection attempt failed because the connected party did not properly respond`

**Solutions:**

1. **Check Gmail App Password:**
   - Ensure `EMAIL_HOST_PASSWORD` is set correctly (16 characters, no spaces)
   - Verify 2-Step Verification is enabled on Gmail account
   - Generate a new App Password if needed

2. **Network/Firewall Issues:**
   - Check if port 587 (TLS) or 465 (SSL) is blocked by firewall
   - Try using a different network (some networks block SMTP)
   - For corporate networks, contact IT to allow SMTP connections

3. **SMTP Settings:**
   - Verify `EMAIL_HOST` is correct (`smtp.gmail.com`)
   - Check `EMAIL_PORT` (587 for TLS, 465 for SSL)
   - Ensure `EMAIL_USE_TLS=True` for port 587
   - Try increasing `EMAIL_TIMEOUT` if connection is slow

4. **Alternative: Use Console Backend for Development:**
   - Remove or comment out `EMAIL_HOST_PASSWORD` in `.env`
   - Emails will be printed to console instead
   - Verification links will be logged for testing

5. **Check Django Logs:**
   - Look for detailed error messages in logs
   - Check if email configuration is loaded correctly

### Token expired

Users can request a new verification email using the send verification endpoint.

### Email already verified

The system will return a message indicating the email is already verified.

### Testing Email Configuration

1. Check console output on server startup - it should show email configuration status
2. Try sending a test email using Django shell:
   ```python
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```
3. Check logs for detailed error messages

## Security Notes

- Tokens expire after 24 hours
- Tokens can only be used once
- Invalid tokens don't reveal if an email exists (security best practice)
- Verification links use secure tokens (32 characters, URL-safe)

