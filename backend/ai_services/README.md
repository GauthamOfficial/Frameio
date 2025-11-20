# AI Services Module

## Overview

The AI Services module provides comprehensive AI integration capabilities for the Frameio platform, including:

- Multi-provider AI service integration (Gemini, OpenAI, Stability AI, Midjourney)
- Rate limiting and security middleware
- Usage quota management
- Template system for AI prompts
- Analytics and monitoring

## Features

### 1. AI Providers
- Support for multiple AI service providers
- Configurable rate limits and API settings
- Provider-specific request handling

### 2. Generation Requests
- Asynchronous AI generation processing
- Request status tracking (pending, processing, completed, failed)
- Result storage and retrieval
- Cost tracking and analytics

### 3. Usage Quotas
- Organization-based quota management
- Multiple quota types (monthly, daily, hourly)
- Automatic usage tracking and enforcement
- Cost and request count limits

### 4. AI Templates
- Reusable prompt templates
- Variable substitution support
- Public and organization-specific templates
- Usage analytics

### 5. Security & Rate Limiting
- Request rate limiting by organization and user
- Content security scanning
- Suspicious prompt detection
- Usage tracking and monitoring

## Models

### AIProvider
Stores AI service provider configurations including API keys, rate limits, and settings.

### AIGenerationRequest
Tracks individual AI generation requests with status, results, and metadata.

### AIUsageQuota
Manages usage quotas per organization, provider, and generation type.

### AITemplate
Stores reusable AI prompt templates with variable substitution.

### AIGenerationHistory
Tracks user feedback and analytics for AI generations.

## API Endpoints

### Providers
- `GET /api/ai/providers/` - List active AI providers
- `GET /api/ai/providers/{id}/` - Get provider details

### Generation Requests
- `POST /api/ai/generation-requests/` - Create new generation request
- `GET /api/ai/generation-requests/` - List organization's requests
- `GET /api/ai/generation-requests/{id}/` - Get request details
- `POST /api/ai/generation-requests/{id}/regenerate/` - Regenerate content
- `POST /api/ai/generation-requests/{id}/rate/` - Rate generation result

### Templates
- `GET /api/ai/templates/` - List available templates
- `POST /api/ai/templates/` - Create new template
- `GET /api/ai/templates/{id}/` - Get template details
- `POST /api/ai/templates/{id}/use_template/` - Use template for generation

### Analytics
- `GET /api/ai/analytics/dashboard/` - Get analytics dashboard data

## Services

### AIGenerationService
Handles processing of AI generation requests across different providers.

### AIPromptEngineeringService
Provides prompt enhancement and optimization for textile-specific use cases.

### AIColorAnalysisService
Analyzes images for color palette extraction and complementary color suggestions.

## Middleware

### RateLimitMiddleware
Implements rate limiting for AI API endpoints based on organization and user.

### AISecurityMiddleware
Scans requests for suspicious content and enforces security policies.

### AIUsageTrackingMiddleware
Tracks API usage for analytics and monitoring.

## Testing

The module includes comprehensive test coverage:

- Model tests for all AI service models
- Service tests for AI processing logic
- API tests for all endpoints
- Integration tests for complete workflows
- Performance tests for bulk operations

Run tests with:
```bash
python manage.py test ai_services
```

## Configuration

Add the following to your Django settings:

```python
INSTALLED_APPS = [
    # ... other apps
    'ai_services',
]

MIDDLEWARE = [
    # ... other middleware
    'ai_services.middleware.RateLimitMiddleware',
    'ai_services.middleware.AISecurityMiddleware',
    'ai_services.middleware.AIUsageTrackingMiddleware',
]
```

## Environment Variables

- `GEMINI_API_KEY` - API key for Gemini service
- `OPENAI_API_KEY` - API key for OpenAI service
- `STABILITY_API_KEY` - API key for Stability AI service

## Usage Examples

### Creating a Generation Request

```python
from ai_services.models import AIProvider, AIGenerationRequest

provider = AIProvider.objects.get(name='gemini')
request = AIGenerationRequest.objects.create(
    organization=organization,
    user=user,
    provider=provider,
    generation_type='poster',
    prompt='Create a beautiful textile design with floral patterns',
    parameters={'width': 1024, 'height': 1024}
)
```

### Using Templates

```python
from ai_services.models import AITemplate

template = AITemplate.objects.create(
    organization=organization,
    name='Floral Design Template',
    category='textile',
    prompt_template='Create a {style} floral design with {colors}',
    default_parameters={'width': 1024, 'height': 1024}
)
```

### Checking Quotas

```python
from ai_services.models import AIUsageQuota

quota = AIUsageQuota.objects.get(
    organization=organization,
    provider=provider,
    generation_type='poster',
    quota_type='monthly'
)

if quota.is_quota_exceeded():
    # Handle quota exceeded
    pass
```

## Best Practices

1. **Rate Limiting**: Always respect rate limits to avoid service disruption
2. **Error Handling**: Implement proper error handling for AI service failures
3. **Quota Management**: Monitor usage quotas to prevent service interruption
4. **Security**: Validate and sanitize all user inputs before processing
5. **Caching**: Cache AI responses when appropriate to reduce costs
6. **Monitoring**: Track usage patterns and performance metrics

## Troubleshooting

### Common Issues

1. **Rate Limit Exceeded**: Check rate limit settings and usage patterns
2. **Quota Exceeded**: Review quota limits and current usage
3. **API Errors**: Verify API keys and provider configurations
4. **Slow Response**: Check AI service status and network connectivity

### Debugging

Enable debug logging:
```python
LOGGING = {
    'loggers': {
        'ai_services': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

