# AI Services Module - NanoBanana Integration

This document covers the NanoBanana AI integration and Phase 1 Week 1 Member 3 deliverables.

## 🎯 Phase 1 Week 1 Member 3 Deliverables

### ✅ Completed Features

1. **Poster Generator with AI Caption Suggestions**
   - Generate textile posters with AI-powered captions
   - Festival-specific caption generation (Deepavali, Pongal, Wedding)
   - Multiple caption variations with effectiveness scoring
   - Fabric-specific prompt enhancement

2. **Catalog Builder with AI Auto-fill Descriptions**
   - Generate product catalogs with AI descriptions
   - Multiple description styles (professional, marketing, technical, lifestyle)
   - Automatic layout generation with various themes
   - Bulk product processing with AI descriptions

3. **Festival Kit Generator with AI Theme Selection**
   - Complete festival kits with multiple posters
   - Festival-specific themes and color palettes
   - Automatic theme matching based on festival type
   - Coordinated design elements across multiple items

4. **Background Matching with Fabric Color Detection**
   - AI-powered fabric color analysis
   - Color harmony and temperature analysis
   - Mood determination based on color psychology
   - Automatic background generation matching fabric colors
   - Multiple background styles (complementary, harmonious, neutral)

## 🚀 NanoBanana AI Integration

### Setup Instructions

1. **Install NanoBanana SDK:**
```bash
pip install banana-dev==6.3.0
```

2. **Configure Environment Variables:**
```bash
# Add to your .env file
NANOBANANA_API_KEY=your-nanobanana-api-key
NANOBANANA_MODEL_KEY=your-deployed-model-key
```

3. **Run Database Migrations:**
```bash
python manage.py migrate
```

4. **Verify Installation:**
```bash
python backend/verify_ai_deliverables.py
```

### NanoBanana Integration Features

- **Real API Integration**: Direct integration with NanoBanana API using banana-dev SDK
- **Fallback System**: Mock data fallback for development when API is unavailable
- **Cost Tracking**: Automatic cost calculation and usage tracking
- **Error Handling**: Comprehensive error handling with logging
- **Rate Limiting**: Built-in rate limiting and quota management

## 📚 API Documentation

### Poster Generation API

#### Generate Poster with Caption
```http
POST /api/ai/poster/generate_poster/
Content-Type: application/json

{
    "fabric_type": "saree",
    "festival": "deepavali",
    "price_range": "₹2999",
    "style": "elegant",
    "color_scheme": "golden",
    "custom_text": "Special Deepavali Collection"
}
```

**Response:**
```json
{
    "success": true,
    "request_id": "uuid-here",
    "poster_urls": ["https://api.nanobanana.com/generated/poster1.png"],
    "caption_suggestions": [
        {
            "text": "✨ Celebrate Deepavali in Style! ✨\nSaree Collection Starting ₹2999\n#Deepavali2024 #FestiveWear",
            "type": "festival_celebration",
            "tone": "festive",
            "effectiveness_score": 9.2
        }
    ],
    "selected_caption": "✨ Celebrate Deepavali in Style! ✨...",
    "cost": 0.05,
    "processing_time": 15.2
}
```

#### Generate Caption Suggestions Only
```http
POST /api/ai/poster/generate_captions/
Content-Type: application/json

{
    "fabric_type": "saree",
    "festival": "deepavali",
    "price_range": "₹2999",
    "style": "elegant"
}
```

### Festival Kit API

#### Generate Festival Kit
```http
POST /api/ai/festival-kit/generate_kit/
Content-Type: application/json

{
    "festival": "deepavali",
    "fabric_types": ["saree", "silk", "cotton"],
    "color_schemes": ["golden", "red and gold", "traditional"],
    "price_ranges": ["₹1999", "₹2999", "₹4999"]
}
```

#### Get Festival Themes
```http
GET /api/ai/festival-kit/themes/?festival=deepavali
```

### Catalog Builder API

#### Build Complete Catalog
```http
POST /api/ai/catalog/build_catalog/
Content-Type: application/json

{
    "products": [
        {
            "name": "Elegant Silk Saree",
            "fabric_type": "silk",
            "color": "golden",
            "price": "₹4999",
            "category": "saree",
            "features": ["handwoven", "pure silk", "traditional design"]
        }
    ],
    "catalog_style": "modern",
    "layout_type": "grid",
    "theme": "professional",
    "auto_generate_descriptions": true
}
```

#### Generate Single Product Description
```http
POST /api/ai/catalog/generate_description/
Content-Type: application/json

{
    "product_info": {
        "name": "Cotton Casual Wear",
        "fabric_type": "cotton",
        "color": "blue",
        "price": "₹1999"
    }
}
```

### Background Matching API

#### Generate Matching Background
```http
POST /api/ai/background/generate_background/
Content-Type: application/json

{
    "fabric_image_url": "https://example.com/fabric.jpg",
    "background_style": "complementary",
    "pattern_type": "seamless",
    "intensity": "medium"
}
```

#### Analyze Fabric Colors
```http
POST /api/ai/background/analyze_colors/
Content-Type: application/json

{
    "fabric_image_url": "https://example.com/fabric.jpg"
}
```

**Response:**
```json
{
    "success": true,
    "color_palette": [
        {
            "hex": "#FF6B6B",
            "rgb": [255, 107, 107],
            "name": "Coral Red",
            "percentage": 35
        }
    ],
    "analysis": {
        "dominant_colors": [...],
        "color_harmony": {
            "type": "complementary",
            "score": 8.5,
            "description": "Opposite colors creating high contrast and visual interest"
        },
        "color_temperature": {
            "temperature": "warm",
            "score": 0.75
        },
        "fabric_mood": {
            "mood": "vibrant",
            "confidence": 0.85,
            "description": "Bold and energetic, great for making a statement"
        }
    }
}
```

## 🧪 Testing

### Run All Tests
```bash
# Run unit tests
python manage.py test ai_services

# Run specific test file
python manage.py test ai_services.test_nanobanana_integration

# Run verification script
python backend/verify_ai_deliverables.py
```

### Test Coverage

The test suite includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end workflow testing
- **API Tests**: REST API endpoint testing
- **Mock Tests**: NanoBanana API integration testing
- **Verification Tests**: Complete deliverable verification

### Sample Test Commands
```bash
# Test poster generation
python manage.py test ai_services.test_nanobanana_integration.TextilePosterGeneratorTestCase

# Test catalog building
python manage.py test ai_services.test_nanobanana_integration.CatalogBuilderTestCase

# Test background matching
python manage.py test ai_services.test_nanobanana_integration.BackgroundMatcherTestCase

# Test API endpoints
python manage.py test ai_services.test_nanobanana_integration.AIServiceAPITestCase
```

## 🏗️ Architecture

### Service Classes

1. **TextilePosterGenerator**
   - Caption generation with multiple variations
   - Festival-specific prompt enhancement
   - Template management and usage tracking

2. **FestivalKitGenerator**
   - Multi-poster festival kit generation
   - Theme and color palette management
   - Coordinated design generation

3. **TextileCatalogBuilder**
   - Product description generation with multiple styles
   - Catalog layout generation
   - Template-based catalog creation

4. **BackgroundMatcher & FabricColorDetector**
   - Advanced color analysis using color theory
   - Mood and temperature analysis
   - Background suggestion generation

5. **AIGenerationService**
   - Core AI service integration
   - Provider management and routing
   - Usage tracking and quota management

## 🎨 Textile-Specific Features

### Festival Support
- **Deepavali**: Golden themes, diyas, rangoli patterns
- **Pongal**: Harvest colors, traditional motifs
- **Wedding**: Auspicious colors, elegant designs

### Fabric Types
- **Saree**: Traditional draping, cultural elements
- **Silk**: Luxury textures, lustrous finishes
- **Cotton**: Natural comfort, breathable designs
- **Linen**: Crisp textures, casual elegance

### Color Analysis
- **Harmony Analysis**: Monochromatic, analogous, complementary, triadic
- **Temperature Analysis**: Warm, cool, neutral classifications
- **Mood Analysis**: Elegant, vibrant, calm, festive, traditional, modern, luxury, casual

## 📊 Usage Examples

### Python Usage

```python
from ai_services.poster_generator import TextilePosterGenerator
from ai_services.catalog_builder import TextileCatalogBuilder
from ai_services.background_matcher import BackgroundMatcher

# Generate poster with caption
poster_gen = TextilePosterGenerator()
result = poster_gen.generate_poster_with_caption(
    organization=organization,
    user=user,
    fabric_type='saree',
    festival='deepavali',
    price_range='₹2999',
    style='elegant'
)

# Build catalog with AI descriptions
catalog_builder = TextileCatalogBuilder()
catalog_result = catalog_builder.build_catalog_with_ai_descriptions(
    organization=organization,
    user=user,
    products=product_list,
    catalog_style='modern'
)

# Generate matching background
bg_matcher = BackgroundMatcher()
bg_result = bg_matcher.generate_matching_background(
    organization=organization,
    user=user,
    fabric_image_url='https://example.com/fabric.jpg',
    background_style='complementary'
)
```

### JavaScript/Frontend Usage

```javascript
// Generate poster
const posterResponse = await fetch('/api/ai/poster/generate_poster/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        fabric_type: 'saree',
        festival: 'deepavali',
        price_range: '₹2999'
    })
});

// Build catalog
const catalogResponse = await fetch('/api/ai/catalog/build_catalog/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        products: productList,
        catalog_style: 'modern'
    })
});

// Analyze fabric colors
const colorResponse = await fetch('/api/ai/background/analyze_colors/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        fabric_image_url: fabricImageUrl
    })
});
```

## 🚀 Deployment

### Production Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set Environment Variables:**
```bash
export NANOBANANA_API_KEY=your-production-api-key
export NANOBANANA_MODEL_KEY=your-production-model-key
```

3. **Run Migrations:**
```bash
python manage.py migrate
```

4. **Create AI Provider:**
```bash
python manage.py shell
>>> from ai_services.models import AIProvider
>>> AIProvider.objects.create(name='nanobanana', api_key='your-key', is_active=True)
```

### Monitoring

- **Usage Tracking**: Monitor API usage and costs
- **Error Logging**: Comprehensive error logging and monitoring
- **Performance Metrics**: Track generation times and success rates
- **Quota Management**: Automatic quota enforcement and alerts

## 🔧 Configuration

### Environment Variables
```bash
# Required
NANOBANANA_API_KEY=your-api-key
NANOBANANA_MODEL_KEY=your-model-key

# Optional
OPENAI_API_KEY=your-openai-key
STABILITY_API_KEY=your-stability-key
```

### Django Settings
```python
# AI Services configuration
NANOBANANA_API_KEY = os.getenv('NANOBANANA_API_KEY', '')
NANOBANANA_MODEL_KEY = os.getenv('NANOBANANA_MODEL_KEY', '')

# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'ai_services',
]
```

## 🎉 Deliverables Summary

All Phase 1 Week 1 Member 3 tasks have been completed:

✅ **Poster Generator**: AI-powered textile poster generation with caption suggestions  
✅ **Catalog Builder**: Auto-fill product descriptions with AI  
✅ **Festival Kit**: Theme-based festival design generation  
✅ **Background Matching**: Fabric color detection and matching backgrounds  
✅ **NanoBanana Integration**: Complete API integration with fallback systems  
✅ **Comprehensive Testing**: Full test suite with verification scripts  
✅ **API Documentation**: Complete REST API documentation  
✅ **Production Ready**: Deployment-ready with monitoring and error handling  

Run `python backend/verify_ai_deliverables.py` to verify all features are working correctly!
