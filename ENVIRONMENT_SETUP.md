# 🔧 Environment Setup Guide

## 📋 Overview

This guide helps you restore and configure the `.env` file for the Frameio AI-Powered Textile Design Platform.

## 🚀 Quick Start

### Option 1: Automated Restoration (Recommended)

**Windows:**
```bash
restore_env.bat
```

**Linux/Mac:**
```bash
python3 restore_env.py
```

### Option 2: Manual Restoration

1. Copy the template file:
   ```bash
   cp env.template .env
   ```

2. Edit the `.env` file with your actual values

## 📝 Environment Variables Explained

### 🔑 Required for Basic Functionality

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `DEBUG` | Debug mode | `True` |
| `DB_NAME` | Database name | `frameio_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | `password` |
| `DB_HOST` | Database host | `localhost` |
| `DB_PORT` | Database port | `5432` |

### 🔐 Authentication (Clerk)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `CLERK_PUBLISHABLE_KEY` | Clerk public key | [Clerk Dashboard](https://dashboard.clerk.com) |
| `CLERK_SECRET_KEY` | Clerk secret key | [Clerk Dashboard](https://dashboard.clerk.com) |
| `NEXT_PUBLIC_CLERK_FRONTEND_API` | Clerk frontend API | [Clerk Dashboard](https://dashboard.clerk.com) |

### 🤖 AI Services

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `NANOBANANA_API_KEY` | NanoBanana API key | [Banana.dev](https://app.banana.dev/) |
| `NANOBANANA_MODEL_KEY` | NanoBanana model key | [Banana.dev](https://app.banana.dev/) |
| `GOOGLE_API_KEY` | Google AI API key | [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_API_KEY` | Gemini API key | [Google AI Studio](https://aistudio.google.com/) |

### 💳 Billing & Payments (Stripe)

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `STRIPE_SECRET_KEY` | Stripe secret key | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |
| `STRIPE_PUBLISHABLE_KEY` | Stripe publishable key | [Stripe Dashboard](https://dashboard.stripe.com/apikeys) |

### 🛡️ Security & Rate Limiting

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `ARCJET_KEY` | Arcjet security key | [Arcjet](https://arcjet.com/) |

### 🗄️ Caching & Storage

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |

## 🔧 Setup Instructions

### 1. Database Setup

**Option A: PostgreSQL (Recommended)**
```bash
# Install PostgreSQL
# Create database
createdb frameio_db

# Update .env with your credentials
DB_NAME=frameio_db
DB_USER=your_username
DB_PASSWORD=your_password
```

**Option B: SQLite (Development)**
```bash
# Comment out PostgreSQL settings in .env
# Uncomment SQLite settings
DATABASE_URL=sqlite:///db.sqlite3
```

### 2. Clerk Authentication Setup

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Create a new application
3. Copy the keys to your `.env` file:
   ```
   CLERK_PUBLISHABLE_KEY=pk_test_...
   CLERK_SECRET_KEY=sk_test_...
   NEXT_PUBLIC_CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev
   ```

### 3. AI Services Setup

**NanoBanana API:**
1. Go to [Banana.dev](https://app.banana.dev/)
2. Create an account and get your API key
3. Update `.env`:
   ```
   NANOBANANA_API_KEY=your_api_key_here
   NANOBANANA_MODEL_KEY=your_model_key_here
   ```

**Google AI (Optional):**
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Get your API key
3. Update `.env`:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

### 4. Stripe Billing (Optional)

1. Go to [Stripe Dashboard](https://dashboard.stripe.com/apikeys)
2. Get your API keys
3. Update `.env`:
   ```
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

### 5. Redis Setup (Optional)

**Install Redis:**
```bash
# Windows (using Chocolatey)
choco install redis

# Linux
sudo apt-get install redis-server

# Mac
brew install redis
```

**Start Redis:**
```bash
redis-server
```

## 🧪 Testing Your Setup

### 1. Check Environment Variables
```bash
python3 restore_env.py
# Choose option 2 to check environment status
```

### 2. Test Database Connection
```bash
cd backend
python manage.py check --database default
```

### 3. Test AI Services
```bash
cd backend
python manage.py test ai_services
```

## 🚨 Troubleshooting

### Common Issues

**1. Database Connection Error**
- Check if PostgreSQL is running
- Verify database credentials in `.env`
- Ensure database exists

**2. Clerk Authentication Error**
- Verify Clerk keys are correct
- Check if Clerk application is active
- Ensure frontend API URL is correct

**3. AI Services Not Working**
- Verify API keys are valid
- Check if services are active
- Review API quotas and limits

**4. Redis Connection Error**
- Ensure Redis is running
- Check Redis URL in `.env`
- Verify Redis port (default: 6379)

### Getting Help

1. Check the logs in `backend/logs/`
2. Run the verification script: `python backend/verify_ai_deliverables.py`
3. Review the implementation summary: `backend/PHASE_1_WEEK_4_AI_IMPLEMENTATION_SUMMARY.md`

## 📚 Additional Resources

- [Django Environment Variables](https://docs.djangoproject.com/en/stable/topics/settings/)
- [Clerk Documentation](https://clerk.com/docs)
- [NanoBanana Documentation](https://docs.banana.dev/)
- [Stripe Documentation](https://stripe.com/docs)
- [Redis Documentation](https://redis.io/docs/)

---

**Note**: Never commit your `.env` file to version control. It contains sensitive information like API keys and passwords.
