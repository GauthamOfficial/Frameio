# Security Best Practices for Frameio

This document outlines the security best practices implemented in the Frameio project to protect sensitive data and API keys.

## 🔐 Environment Variables Security

### ✅ What We've Implemented

1. **Removed Hardcoded Keys**: All API keys and sensitive data have been removed from `settings.py`
2. **Environment Variable Validation**: Added comprehensive validation for required environment variables
3. **Secure Template**: Updated `.env.template` with placeholder values instead of real keys
4. **Secret Key Generation**: Created a script to generate secure Django secret keys

### 🛡️ Security Measures

#### 1. Environment Variables Only
- All sensitive configuration is now loaded from environment variables
- No hardcoded secrets in the codebase
- Proper validation with helpful error messages

#### 2. Required vs Optional Variables
- **Required**: `SECRET_KEY` (Django will not start without it)
- **Optional but Recommended**: `GEMINI_API_KEY`, `CLERK_*` keys
- Graceful degradation when optional keys are missing

#### 3. Development vs Production
- Development: Warnings for missing optional keys
- Production: Errors for missing required keys

## 📋 Environment Setup

### 1. Copy the Template
```bash
cp env.template .env
```

### 2. Generate a Secret Key
```bash
cd backend
python generate_secret_key.py
```

### 3. Update Your .env File
Replace all `your_*_key_here` placeholders with actual values:

```env
# Required
SECRET_KEY=your_generated_secret_key_here

# Optional but recommended
GEMINI_API_KEY=your_gemini_api_key_here
CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
CLERK_SECRET_KEY=your_clerk_secret_key_here
NEXT_PUBLIC_CLERK_FRONTEND_API=your_clerk_frontend_api_url_here
```

## 🔒 API Key Management

### Google Gemini API
1. Visit: https://aistudio.google.com/app/apikey
2. Create a new API key
3. Add to your `.env` file as `GEMINI_API_KEY`

### Clerk Authentication
1. Visit: https://dashboard.clerk.com
2. Create a new application
3. Copy the keys to your `.env` file

### Arcjet (Optional)
1. Visit: https://arcjet.com/
2. Get your API key
3. Add to your `.env` file as `ARCJET_KEY`

## 🚨 Security Checklist

### Before Deployment
- [ ] All API keys are in environment variables
- [ ] No hardcoded secrets in code
- [ ] `.env` file is in `.gitignore`
- [ ] Production uses different keys than development
- [ ] Secret key is unique and secure
- [ ] Database credentials are secure
- [ ] CORS settings are properly configured

### Regular Maintenance
- [ ] Rotate API keys periodically
- [ ] Monitor for exposed secrets in logs
- [ ] Review access permissions
- [ ] Update dependencies regularly
- [ ] Audit environment variables

## 🛠️ Development Tools

### Generate New Secret Key
```bash
cd backend
python generate_secret_key.py
```

### Validate Environment
The application will automatically validate environment variables on startup and provide helpful error messages.

### Check for Exposed Keys
```bash
# Search for potential hardcoded keys (run from project root)
grep -r "sk_" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "pk_" . --exclude-dir=node_modules --exclude-dir=.git
grep -r "AIza" . --exclude-dir=node_modules --exclude-dir=.git
```

## 📁 File Security

### Files to Never Commit
- `.env` (contains real API keys)
- `*.key` (private key files)
- `secrets.json` (if used)
- Any file containing actual API keys

### Files Safe to Commit
- `env.template` (contains only placeholders)
- `settings.py` (no hardcoded secrets)
- `generate_secret_key.py` (utility script)

## 🔍 Monitoring

### Log Monitoring
The application logs warnings for missing optional configuration:
```
WARNING: GEMINI_API_KEY not configured. AI services will not be available.
INFO: Optional environment variables not set: CLERK_PUBLISHABLE_KEY, CLERK_SECRET_KEY
```

### Error Handling
- Missing required variables cause startup failure in production
- Missing optional variables show warnings in development
- Clear error messages guide developers to fix configuration

## 🚀 Production Deployment

### Environment Variables in Production
Use your hosting platform's environment variable management:
- **Heroku**: `heroku config:set SECRET_KEY=your_key`
- **AWS**: Use AWS Secrets Manager or Parameter Store
- **Docker**: Use Docker secrets or environment files
- **Kubernetes**: Use Kubernetes secrets

### Security Headers
Ensure your production setup includes:
- HTTPS enforcement
- Security headers (HSTS, CSP, etc.)
- Rate limiting
- Input validation
- SQL injection protection

## 📞 Support

If you encounter issues with environment configuration:
1. Check the error messages in the console
2. Verify your `.env` file format
3. Ensure all required variables are set
4. Test with the validation script

Remember: **Never commit real API keys to version control!**






