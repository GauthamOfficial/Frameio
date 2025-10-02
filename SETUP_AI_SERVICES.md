# 🚀 Setup Guide: Phase 1 Week 1 Member 3 AI Services

This guide will help you get all the AI services working on your site.

## 📋 Prerequisites

Make sure you have:
- Python 3.8+ installed
- Django project running
- Virtual environment activated

## 🔧 Step-by-Step Setup

### Step 1: Activate Virtual Environment
```bash
# Windows
startup_env\Scripts\activate

# macOS/Linux
source startup_env/bin/activate
```

### Step 2: Install Required Dependencies
```bash
# Install NanoBanana SDK
pip install banana-dev==6.3.0

# Verify installation
pip list | grep banana
```

### Step 3: Configure Environment Variables
Create or update your `.env` file in the project root:
```bash
# AI Services Configuration
NANOBANANA_API_KEY=your-nanobanana-api-key-here
NANOBANANA_MODEL_KEY=your-nanobanana-model-key-here

# Optional: For development, you can use test keys
# NANOBANANA_API_KEY=test-key-for-development
# NANOBANANA_MODEL_KEY=test-model-key
```

### Step 4: Run Database Migrations
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Setup AI Services
```bash
# Run the setup script
python backend/setup_ai_services.py
```

This script will:
- Create NanoBanana AI provider
- Set up test organization and user
- Create AI templates
- Configure usage quotas
- Verify all services are working

### Step 6: Start the Django Server
```bash
# Make sure you're in the backend directory
cd backend
python manage.py runserver
```

### Step 7: Test the AI Services
In a new terminal, run:
```bash
# Test all AI endpoints
python backend/test_ai_endpoints.py
```

## 🧪 Quick Test

Once the server is running, test the AI services:

### Test 1: Generate Captions
```bash
curl -X POST http://localhost:8000/api/ai/poster/generate_captions/ \
  -H "Content-Type: application/json" \
  -d '{"fabric_type": "saree", "festival": "deepavali", "price_range": "₹2999"}'
```

**Expected Response:**
```json
{
  "success": true,
  "caption_suggestions": [
    {
      "text": "✨ Celebrate Deepavali in Style! ✨\nSaree Collection Starting ₹2999\n#Deepavali2024 #FestiveWear",
      "type": "festival_celebration",
      "tone": "festive",
      "effectiveness_score": 9.2
    }
  ]
}
```

### Test 2: Get Festival Themes
```bash
curl -X GET "http://localhost:8000/api/ai/festival-kit/themes/?festival=deepavali"
```

### Test 3: Get Background Presets
```bash
curl -X GET http://localhost:8000/api/ai/background/presets/
```

## 🎯 Available AI Services

### 1. Poster Generator
- **Endpoint**: `/api/ai/poster/`
- **Features**: AI caption generation, poster creation
- **Festivals**: Deepavali, Pongal, Wedding

### 2. Festival Kit Generator
- **Endpoint**: `/api/ai/festival-kit/`
- **Features**: Complete festival kits, themes, color palettes

### 3. Catalog Builder
- **Endpoint**: `/api/ai/catalog/`
- **Features**: AI product descriptions, catalog layouts

### 4. Background Matcher
- **Endpoint**: `/api/ai/background/`
- **Features**: Color analysis, background generation

## 🔍 Troubleshooting

### Issue 1: "Module not found" errors
**Solution:**
```bash
# Make sure you're in the right directory and virtual environment is activated
cd backend
startup_env\Scripts\activate  # Windows
python manage.py shell
>>> import ai_services
>>> print("AI services imported successfully!")
```

### Issue 2: Database errors
**Solution:**
```bash
# Reset and recreate migrations
cd backend
python manage.py makemigrations ai_services
python manage.py migrate
```

### Issue 3: API endpoints not found
**Solution:**
```bash
# Check URL configuration
python manage.py show_urls | grep ai
```

### Issue 4: Server not starting
**Solution:**
```bash
# Check for port conflicts
python manage.py runserver 8001  # Try different port
```

## 📊 Verification Checklist

Run this checklist to ensure everything is working:

- [ ] Virtual environment activated
- [ ] Dependencies installed (`pip list | grep banana`)
- [ ] Environment variables set
- [ ] Database migrations applied
- [ ] Django server running on http://localhost:8000
- [ ] AI endpoints responding (run `python backend/test_ai_endpoints.py`)
- [ ] Caption generation working
- [ ] Festival themes loading
- [ ] Catalog templates available
- [ ] Background presets loading

## 🎉 Success Indicators

You'll know everything is working when:

1. **Server Status**: http://localhost:8000/ returns API status
2. **AI Endpoints**: All endpoints return 200 status codes
3. **Caption Generation**: Returns multiple caption suggestions
4. **Festival Themes**: Returns theme and color palette data
5. **Templates**: Returns available templates
6. **Background Presets**: Returns preset configurations

## 🔗 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ai/poster/generate_poster/` | POST | Generate complete poster with captions |
| `/api/ai/poster/generate_captions/` | POST | Generate captions only |
| `/api/ai/festival-kit/generate_kit/` | POST | Generate festival kit |
| `/api/ai/festival-kit/themes/` | GET | Get festival themes |
| `/api/ai/catalog/build_catalog/` | POST | Build product catalog |
| `/api/ai/catalog/generate_description/` | POST | Generate product description |
| `/api/ai/catalog/templates/` | GET | Get catalog templates |
| `/api/ai/background/generate_background/` | POST | Generate matching background |
| `/api/ai/background/analyze_colors/` | POST | Analyze fabric colors |
| `/api/ai/background/presets/` | GET | Get background presets |

## 🆘 Need Help?

If you're still having issues:

1. **Check the logs**: Look at the Django console output for error messages
2. **Run the verification script**: `python backend/verify_ai_deliverables.py`
3. **Test individual components**: Use the test files in `backend/ai_services/`
4. **Check database**: Ensure all migrations are applied

## 🎊 Final Verification

Run this command to verify everything is working:
```bash
python backend/verify_ai_deliverables.py
```

This will test all AI services and generate a detailed report.

**Expected Output:**
```
🎉 ALL DELIVERABLES VERIFIED SUCCESSFULLY!
✅ Phase 1 Week 1 Member 3 tasks are complete and working
```

Once you see this message, all your AI services are ready to use! 🚀
