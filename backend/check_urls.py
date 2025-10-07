#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.urls import reverse
from django.core.urlresolvers import get_resolver

# Get all URL patterns
resolver = get_resolver()
url_patterns = []

def extract_urls(urlpatterns, prefix=''):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            extract_urls(pattern.url_patterns, prefix + str(pattern.pattern))
        else:
            url_patterns.append(prefix + str(pattern.pattern))

extract_urls(resolver.url_patterns)

# Print all URL patterns
print("Available URL patterns:")
for pattern in sorted(url_patterns):
    if 'textile' in pattern or 'schedule' in pattern:
        print(f"  {pattern}")

# Try to reverse some URLs
try:
    print("\nTrying to reverse URLs:")
    print(f"textile-poster-new-generate-poster: {reverse('textile-poster-new-generate-poster')}")
except Exception as e:
    print(f"Error reversing textile-poster-new-generate-poster: {e}")

try:
    print(f"textile-caption-generate-caption: {reverse('textile-caption-generate-caption')}")
except Exception as e:
    print(f"Error reversing textile-caption-generate-caption: {e}")

try:
    print(f"scheduled-post-list: {reverse('scheduled-post-list')}")
except Exception as e:
    print(f"Error reversing scheduled-post-list: {e}")
