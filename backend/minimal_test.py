#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

try:
    from ai_services.social_media import SocialMediaService
    print("✅ SocialMediaService import successful")
    
    service = SocialMediaService()
    result = service.post_to_facebook('https://example.com/image.jpg', 'Test caption')
    print(f"✅ Facebook post test: {result['success']}")
    
except Exception as e:
    print(f"❌ SocialMediaService test failed: {e}")

try:
    from ai_services.arcjet_service import ArcjetService
    print("✅ ArcjetService import successful")
    
    service = ArcjetService()
    print("✅ ArcjetService created successfully")
    
except Exception as e:
    print(f"❌ ArcjetService test failed: {e}")

try:
    from ai_services.scheduling_models import ScheduledPost
    print("✅ ScheduledPost model import successful")
    
except Exception as e:
    print(f"❌ ScheduledPost model test failed: {e}")

try:
    from ai_services.textile_views import TextilePosterViewSet, TextileCaptionViewSet
    print("✅ Textile views import successful")
    
except Exception as e:
    print(f"❌ Textile views test failed: {e}")

print("🎉 Basic imports and functionality test completed!")
