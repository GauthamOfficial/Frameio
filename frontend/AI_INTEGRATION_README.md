# AI Integration for Frameio - Phase 1 Week 3

This document provides comprehensive documentation for the AI integration features implemented in the Frameio textile marketing automation platform.

## 🎯 Overview

The AI integration adds powerful capabilities to the poster generator, including:
- **NanoBanana API integration** for AI image generation
- **Intelligent prompt engineering** for textile-specific content
- **Color palette extraction** from uploaded images
- **Template recommendation system** based on AI analysis
- **Robust error handling** with fallback mechanisms

## 🏗️ Architecture

```
frontend/src/
├── lib/ai/
│   ├── nanobanana.ts          # NanoBanana API service
│   ├── promptUtils.ts         # Textile prompt engineering
│   ├── errorHandler.ts        # Error handling & fallbacks
│   └── __tests__/
│       └── ai-integration.test.ts
├── components/
│   ├── ColorPaletteExtractor.tsx    # Color extraction component
│   ├── TemplateRecommender.tsx      # Template recommendation
│   └── lazy/
│       └── enhanced-poster-generator.tsx  # Main AI-integrated component
└── scripts/
    └── verify-ai-integration.js     # Verification script
```

## 🚀 Features

### 1. NanoBanana API Integration

**File:** `src/lib/ai/nanobanana.ts`

- **Image Generation**: Generate high-quality images using NanoBanana's AI models
- **Prompt Enhancement**: Automatically enhance prompts with textile-specific keywords
- **Fallback System**: Graceful fallback to static images when API is unavailable
- **Error Handling**: Comprehensive error handling with retry logic

**Key Methods:**
```typescript
// Generate image with enhanced prompt
const response = await nanoBananaService.generateImage(prompt, options);

// Check service availability
const isConfigured = nanoBananaService.isConfigured();

// Get fallback response
const fallback = nanoBananaService.getFallbackResponse(prompt, options);
```

### 2. AI Prompt Engineering

**File:** `src/lib/ai/promptUtils.ts`

- **Textile-Aware Prompts**: Generate prompts optimized for textile marketing
- **Keyword Extraction**: Extract relevant keywords from user input
- **Prompt Validation**: Validate and score prompt quality
- **Multi-Variation Generation**: Create multiple prompt variations

**Key Functions:**
```typescript
// Generate textile-specific prompt
const prompt = generateTextilePrompt({
  theme: 'festive saree collection',
  color: 'maroon gold',
  style: 'minimal',
  fabric: 'silk',
  occasion: 'wedding'
});

// Extract keywords from user input
const keywords = extractKeywordsFromInput('red cotton saree for wedding');

// Validate prompt quality
const validation = validatePrompt(prompt);
```

### 3. Color Palette Extraction

**File:** `src/components/ColorPaletteExtractor.tsx`

- **Canvas-Based Extraction**: Extract dominant colors using HTML5 Canvas
- **Color Quantization**: Reduce noise by quantizing similar colors
- **Visual Display**: Show color swatches with hex codes and percentages
- **Export Functionality**: Download palette as JSON or copy individual colors

**Features:**
- Real-time color extraction from uploaded images
- Interactive color swatches with hover effects
- Color copying to clipboard
- Palette download functionality
- Responsive design for all screen sizes

### 4. Template Recommendation System

**File:** `src/components/TemplateRecommender.tsx`

- **AI-Powered Matching**: Recommend templates based on theme, colors, and style
- **Scoring Algorithm**: Calculate relevance scores for template matching
- **Mock Data**: Comprehensive template database with metadata
- **Interactive Selection**: Preview and select recommended templates

**Template Matching:**
- Style matching (40% weight)
- Theme/tag matching (30% weight)
- Color matching (20% weight)
- Popularity bonus (10% weight)

### 5. Enhanced Error Handling

**File:** `src/lib/ai/errorHandler.ts`

- **Retry Logic**: Exponential backoff retry mechanism
- **Fallback System**: Automatic fallback to alternative services
- **Error Categorization**: Categorize errors for appropriate handling
- **User-Friendly Messages**: Convert technical errors to user-friendly messages

**Error Types:**
- `NETWORK_ERROR`: Network connectivity issues
- `TIMEOUT_ERROR`: Request timeout errors
- `AUTH_ERROR`: Authentication failures
- `RATE_LIMIT_ERROR`: API rate limiting
- `SERVER_ERROR`: Server-side errors
- `QUOTA_ERROR`: API quota exceeded

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file with the following variables:

```bash
# NanoBanana API Configuration
NEXT_PUBLIC_NANOBANANA_API_KEY=your_api_key_here
NEXT_PUBLIC_NANOBANANA_BASE_URL=https://api.nanobanana.ai/v1/

# Next.js Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Dependencies

The following dependencies are required:

```json
{
  "dependencies": {
    "axios": "^1.12.2",
    "color-thief": "^2.3.0",
    "lucide-react": "^0.544.0"
  }
}
```

## 🧪 Testing

### Running Tests

```bash
# Run AI integration tests
npm test src/lib/ai/__tests__/ai-integration.test.ts

# Run verification script
node scripts/verify-ai-integration.js
```

### Test Coverage

The test suite covers:
- NanoBanana service functionality
- Prompt engineering utilities
- Error handling mechanisms
- Color extraction algorithms
- Template recommendation logic
- End-to-end integration workflows

## 🚀 Usage

### Basic Usage

1. **Navigate to Poster Generator**: Go to `/dashboard/poster-generator`
2. **Enter Prompt**: Describe your textile design
3. **Select Options**: Choose style, fabric, and occasion
4. **Generate**: Click "Generate with AI" button
5. **Extract Colors**: View extracted color palette
6. **Get Recommendations**: See AI-recommended templates

### Advanced Usage

```typescript
// Custom AI generation
import { nanoBananaService } from '@/lib/ai/nanobanana';
import { generateTextilePrompt } from '@/lib/ai/promptUtils';

const prompt = generateTextilePrompt({
  theme: 'luxury silk collection',
  style: 'elegant',
  fabric: 'silk',
  occasion: 'wedding'
});

const response = await nanoBananaService.generateImage(
  prompt.enhancedPrompt,
  {
    style: 'elegant',
    quality: 'hd',
    aspect_ratio: '1:1'
  }
);
```

## 🔍 Verification

### Manual Verification Steps

1. **Generate Image**: Create an image using NanoBanana API
2. **Extract Colors**: Verify color palette extraction works
3. **Template Recommendations**: Check template suggestions appear
4. **Error Handling**: Test API failure fallback
5. **Responsive UI**: Verify mobile compatibility

### Automated Verification

Run the verification script:

```bash
node scripts/verify-ai-integration.js
```

This script checks:
- File existence and structure
- Code implementation completeness
- Dependency configuration
- Environment setup
- Test coverage

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Found**
   - Ensure `NEXT_PUBLIC_NANOBANANA_API_KEY` is set in `.env.local`
   - Check API key validity with NanoBanana service

2. **Color Extraction Fails**
   - Verify image is properly loaded
   - Check CORS settings for external images
   - Ensure canvas is supported in browser

3. **Template Recommendations Not Showing**
   - Check if theme/prompt is provided
   - Verify color palette extraction completed
   - Ensure template data is loaded

4. **Error Handling Not Working**
   - Check error handler configuration
   - Verify fallback assets are available
   - Review console for error details

### Debug Mode

Enable debug logging by setting:

```bash
NODE_ENV=development
```

This will show detailed error logs and API responses in the console.

## 📊 Performance

### Optimization Features

- **Lazy Loading**: Components loaded on demand
- **Image Caching**: Generated images cached for reuse
- **Error Recovery**: Automatic retry with exponential backoff
- **Fallback Assets**: Pre-loaded static images for offline use

### Monitoring

The error handler provides statistics:

```typescript
import { aiErrorHandler } from '@/lib/ai/errorHandler';

const stats = aiErrorHandler.getErrorStats();
console.log('Error statistics:', stats);
```

## 🔮 Future Enhancements

### Planned Features

1. **Advanced Color Analysis**: HSL/LAB color space analysis
2. **ML-Based Recommendations**: Machine learning for template matching
3. **Batch Processing**: Generate multiple images simultaneously
4. **Custom Models**: Fine-tuned models for textile-specific generation
5. **Analytics Dashboard**: Usage statistics and performance metrics

### Integration Opportunities

- **Backend ML Models**: Replace mock data with real ML recommendations
- **Third-Party APIs**: Integrate additional AI services
- **Real-Time Collaboration**: Multi-user AI generation sessions
- **Mobile App**: React Native version with AI features

## 📝 API Reference

### NanoBanana Service

```typescript
interface NanoBananaOptions {
  model?: string;
  style?: string;
  quality?: 'standard' | 'hd';
  aspect_ratio?: '1:1' | '16:9' | '9:16' | '4:3' | '3:4';
  seed?: number;
  steps?: number;
  guidance_scale?: number;
}

interface NanoBananaResponse {
  success: boolean;
  image_url?: string;
  error?: string;
  metadata?: {
    model: string;
    prompt: string;
    generated_at: string;
    processing_time: number;
  };
}
```

### Prompt Utils

```typescript
interface TextilePromptParams {
  theme: string;
  color?: string;
  style?: string;
  fabric?: string;
  occasion?: string;
  mood?: string;
  additionalKeywords?: string[];
}

interface GeneratedPrompt {
  prompt: string;
  enhancedPrompt: string;
  keywords: string[];
  metadata: {
    theme: string;
    style: string;
    colorScheme: string;
    generated_at: string;
  };
}
```

### Color Palette

```typescript
interface ColorInfo {
  hex: string;
  rgb: [number, number, number];
  hsl: [number, number, number];
  percentage: number;
  name?: string;
}
```

## 🤝 Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables
4. Run development server: `npm run dev`
5. Run tests: `npm test`

### Code Style

- Use TypeScript for all new code
- Follow existing component patterns
- Add tests for new features
- Update documentation for API changes

### Pull Request Process

1. Create feature branch
2. Implement changes with tests
3. Run verification script
4. Update documentation
5. Submit pull request

## 📄 License

This AI integration is part of the Frameio project and follows the same licensing terms.

---

**Last Updated:** January 2024  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
