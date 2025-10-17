#!/usr/bin/env python3
"""
Run Branding Test
Quick test to verify that automatic branding is working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from test_automatic_branding import main

if __name__ == "__main__":
    print("🚀 Running Automatic Branding Test...")
    print("This will test that company logos and contact details are automatically added to generated posters.")
    print("=" * 70)
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Automatic branding is working correctly!")
        print("✅ Company logos and contact details are automatically added to generated posters")
        print("✅ Users can see their branding preview before generating posters")
        print("✅ The system fetches business data from settings and applies it to posters")
    else:
        print("\n❌ FAILED! Automatic branding is not working correctly")
        print("❌ Please check the error messages above and fix the issues")
    
    sys.exit(0 if success else 1)

