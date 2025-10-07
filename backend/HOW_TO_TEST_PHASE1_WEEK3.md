# How to Test Phase 1 Week 3 Features

## 🚀 Quick Start

### 1. Setup Test Data
```bash
cd backend
python quick_start.py
```

### 2. Start the Server
```bash
python manage.py runserver
```

### 3. Test the Features
Open your browser and go to: `http://localhost:8000/simple_test_interface.html`

## 📋 What You Can Test

### 🎨 Textile Poster Generation
- **Endpoint**: `POST /api/ai/textile/poster/generate_poster/`
- **Features**: AI-powered poster generation with festival themes
- **Input**: Product image, fabric type, festival, price range, style
- **Output**: Generated poster URL, captions, hashtags

### 📝 Textile Caption Generation  
- **Endpoint**: `POST /api/ai/textile/caption/generate_caption/`
- **Features**: AI-generated captions and hashtags
- **Input**: Product name, fabric type, festival, style
- **Output**: Multiple caption suggestions, relevant hashtags

### 📅 Social Media Scheduling
- **Endpoint**: `POST /api/ai/schedule/`
- **Features**: Schedule posts for Facebook, Instagram, TikTok, etc.
- **Input**: Platform, asset URL, caption, scheduled time
- **Output**: Scheduled post confirmation

### 📊 Analytics
- **Endpoint**: `GET /api/ai/schedule/analytics/`
- **Features**: View scheduling statistics and performance
- **Output**: Analytics data and insights

## 🔐 Authentication

### Test Credentials
- **Username**: `testuser`
- **Password**: `testpass123`
- **Organization**: `test-org`

### API Headers
When making API calls, include these headers:
```
Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=
X-Organization: test-org
Content-Type: application/json
```

## 🧪 Example API Calls

### Test Poster Generation
```bash
curl -X POST http://localhost:8000/api/ai/textile/poster/generate_poster/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=" \
  -H "X-Organization: test-org" \
  -d '{
    "product_image_url": "https://example.com/product.jpg",
    "fabric_type": "saree",
    "festival": "deepavali",
    "price_range": "₹2999",
    "style": "elegant"
  }'
```

### Test Caption Generation
```bash
curl -X POST http://localhost:8000/api/ai/textile/caption/generate_caption/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=" \
  -H "X-Organization: test-org" \
  -d '{
    "product_name": "Elegant Silk Saree",
    "fabric_type": "silk",
    "festival": "deepavali",
    "price_range": "₹4999",
    "style": "traditional"
  }'
```

### Test Schedule Creation
```bash
curl -X POST http://localhost:8000/api/ai/schedule/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic dGVzdHVzZXI6dGVzdHBhc3MxMjM=" \
  -H "X-Organization: test-org" \
  -d '{
    "platform": "facebook",
    "asset_url": "https://example.com/image.jpg",
    "caption": "Test scheduled post",
    "scheduled_time": "2024-12-31T12:00:00Z"
  }'
```

## 🎯 Features Implemented

### ✅ Product-to-Poster Workflow
- AI-powered textile poster generation
- Festival-specific themes (Deepavali, Pongal, Wedding)
- Fabric type support (Saree, Cotton, Silk, Linen, Wool, Denim)
- Style options (Elegant, Modern, Traditional, Bohemian, Casual)
- Custom text and offer details integration

### ✅ Scheduling System
- Complete CRUD operations for scheduled posts
- Support for all major social media platforms
- Status management (pending, scheduled, posted, failed, cancelled)
- Retry mechanism for failed posts
- Analytics and reporting

### ✅ Social Media Integration
- Placeholder services for all platforms
- Facebook, Instagram, TikTok, WhatsApp, Twitter, LinkedIn
- Structured for easy real API integration
- Error handling and response formatting

### ✅ Usage Limits (Arcjet Integration)
- Plan-based usage limits (Free, Premium, Enterprise)
- Service-specific limits for different features
- Usage tracking and increment
- Graceful error handling when limits exceeded

## 🔧 Troubleshooting

### Server Not Starting
1. Check if port 8000 is available
2. Make sure Django is properly installed
3. Run `python manage.py check` to verify setup

### Authentication Issues
1. Make sure test user exists: `python quick_start.py`
2. Check organization membership
3. Verify headers are correct

### Endpoint Not Found
1. Check if server is running on correct port
2. Verify URL patterns in `ai_services/urls.py`
3. Check Django URL configuration

### Database Issues
1. Run migrations: `python manage.py migrate`
2. Check database connection
3. Verify models are properly defined

## 📞 Support

If you encounter any issues:
1. Check the test interface at `http://localhost:8000/simple_test_interface.html`
2. Review the test report: `PHASE_1_WEEK_3_TEST_REPORT.md`
3. Run the verification script: `python verify_phase1_week3.py`

## 🎉 Success Indicators

You'll know everything is working when:
- ✅ Server starts without errors
- ✅ Test interface loads and shows endpoints
- ✅ API calls return 200 status codes
- ✅ Generated content includes AI-powered results
- ✅ Scheduling system creates and manages posts
- ✅ Usage limits are enforced properly
