#!/usr/bin/env python3
"""
Run Enhanced Branding Test
Test the new approach where company logos and contact details are integrated into AI generation.
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

from test_enhanced_branding import main

if __name__ == "__main__":
    print("🚀 Running Enhanced Branding Test...")
    print("This will test the new approach where company logos and contact details are integrated into AI generation.")
    print("=" * 80)
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Enhanced branding approach is working correctly!")
        print("✅ Company logos and contact details are integrated into AI generation")
        print("✅ No post-processing overlay needed - branding is built into the design")
        print("✅ AI naturally incorporates company branding into the poster layout")
    else:
        print("\n❌ FAILED! Enhanced branding approach is not working correctly")
        print("❌ Please check the error messages above and fix the issues")
    
    sys.exit(0 if success else 1)
