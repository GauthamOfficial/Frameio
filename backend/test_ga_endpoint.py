#!/usr/bin/env python3
"""
Test the Google Analytics endpoint directly
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from ai_services.google_analytics_service import get_google_analytics_service

print("=" * 60)
print("Testing Google Analytics Service from Django")
print("=" * 60)

ga_service = get_google_analytics_service()

print(f"\nProperty ID: {ga_service.property_id}")
print(f"Client initialized: {ga_service.client is not None}")
print(f"Is configured: {ga_service.is_configured()}")

if ga_service.is_configured():
    print("\n[OK] Service is configured!")
    try:
        # Test fetching data
        print("\nTesting overview stats...")
        overview = ga_service.get_overview_stats(days=30)
        if 'error' in overview:
            print(f"[ERROR] {overview['error']}")
        else:
            print(f"[OK] Overview stats retrieved:")
            print(f"  - Total Users: {overview.get('totalUsers', 'N/A')}")
            print(f"  - Page Views: {overview.get('pageViews', 'N/A')}")
    except Exception as e:
        print(f"[ERROR] Failed to fetch data: {str(e)}")
        import traceback
        traceback.print_exc()
else:
    print("\n[ERROR] Service is NOT configured")
    print("Check the initialization logs above")

print("\n" + "=" * 60)

