#!/usr/bin/env python3
"""
Run Branding Service Test
Test just the branding service without requiring AI generation.
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

from test_branding_service_only import main

if __name__ == "__main__":
    print("🚀 Running Branding Service Test...")
    print("This will test the branding service without requiring AI generation.")
    print("=" * 80)
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Branding service is working correctly!")
        print("✅ Company logos and contact details are integrated into prompts")
        print("✅ Enhanced prompts include all branding requirements")
        print("✅ The branding approach is ready for AI generation")
    else:
        print("\n❌ FAILED! Branding service is not working correctly")
        print("❌ Please check the error messages above and fix the issues")
    
    sys.exit(0 if success else 1)
