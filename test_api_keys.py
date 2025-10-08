#!/usr/bin/env python3
"""
Test script to verify API keys configuration
"""
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_api_keys():
    """Test API keys configuration"""
    print('=== API Keys Configuration Test ===')
    
    # Test environment variables
    env_vars = {
        'ARCJET_KEY': os.getenv('ARCJET_KEY'),
        'NANOBANANA_API_KEY': os.getenv('NANOBANANA_API_KEY'),
        'NANOBANANA_MODEL_KEY': os.getenv('NANOBANANA_MODEL_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY'),
        'GEMINI_MODEL_NAME': os.getenv('GEMINI_MODEL_NAME'),
        'CLERK_PUBLISHABLE_KEY': os.getenv('CLERK_PUBLISHABLE_KEY'),
        'CLERK_SECRET_KEY': os.getenv('CLERK_SECRET_KEY'),
        'NEXT_PUBLIC_CLERK_FRONTEND_API': os.getenv('NEXT_PUBLIC_CLERK_FRONTEND_API'),
    }
    
    for key, value in env_vars.items():
        status = "✓ Set" if value else "✗ Missing"
        print(f'{key}: {status}')
        if value and (key.startswith('NANOBANANA') or key.startswith('GEMINI') or key.startswith('GOOGLE')):
            print(f'  Value: {value[:20]}...' if len(value) > 20 else f'  Value: {value}')
    
    # Test Django settings
    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
        django.setup()
        
        from django.conf import settings
        print('\n=== Django Settings Test ===')
        
        django_settings = {
            'ARCJET_KEY': getattr(settings, 'ARCJET_KEY', None),
            'NANOBANANA_API_KEY': getattr(settings, 'NANOBANANA_API_KEY', None),
            'NANOBANANA_MODEL_KEY': getattr(settings, 'NANOBANANA_MODEL_KEY', None),
            'GOOGLE_API_KEY': getattr(settings, 'GOOGLE_API_KEY', None),
            'GEMINI_API_KEY': getattr(settings, 'GEMINI_API_KEY', None),
            'GEMINI_MODEL_NAME': getattr(settings, 'GEMINI_MODEL_NAME', None),
            'CLERK_CONFIGURED': getattr(settings, 'CLERK_CONFIGURED', False),
        }
        
        for key, value in django_settings.items():
            if key == 'CLERK_CONFIGURED':
                status = "✓" if value else "✗"
                print(f'{key}: {status}')
            else:
                status = "✓" if value else "✗"
                print(f'{key}: {status}')
                if value and (key.startswith('NANOBANANA') or key.startswith('GEMINI') or key.startswith('GOOGLE')):
                    print(f'  Value: {value[:20]}...' if len(value) > 20 else f'  Value: {value}')
        
        # Test AI services
        print('\n=== AI Services Test ===')
        try:
            from ai_services.models import AIProvider
            
            # Test NanoBanana provider
            nanobanana_providers = AIProvider.objects.filter(name='nanobanana')
            if nanobanana_providers.exists():
                provider = nanobanana_providers.first()
                print(f'✓ NanoBanana provider found: {provider.name}')
                print(f'  Active: {provider.is_active}')
                print(f'  Has API key: {"✓" if provider.api_key else "✗"}')
            else:
                print('✗ NanoBanana provider not found')
            
            # Test Gemini provider
            gemini_providers = AIProvider.objects.filter(name='gemini')
            if gemini_providers.exists():
                provider = gemini_providers.first()
                print(f'✓ Gemini provider found: {provider.name}')
                print(f'  Active: {provider.is_active}')
                print(f'  Has API key: {"✓" if provider.api_key else "✗"}')
                print(f'  Model: {provider.model_key}')
            else:
                print('✗ Gemini provider not found')
                
        except Exception as e:
            print(f'✗ AI Services test failed: {e}')
            
    except Exception as e:
        print(f'Django setup error: {e}')
        return False
    
    return True

if __name__ == '__main__':
    test_api_keys()
