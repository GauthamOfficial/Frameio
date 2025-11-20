#!/usr/bin/env python3
"""
Run Branding Fix Test
Test that the branding fix is working correctly.
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

from test_branding_fix import main

if __name__ == "__main__":
    print("🚀 Running Branding Fix Test...")
    print("This will test that company logos and contact details are properly applied to generated posters.")
    print("=" * 70)
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Branding fix is working correctly!")
        print("✅ Company logos and contact details are automatically added to generated posters")
        print("✅ The has_complete_profile property now works with only WhatsApp and Email")
        print("✅ Brand overlay service is applying logos and contact information correctly")
    else:
        print("\n❌ FAILED! Branding fix is not working correctly")
        print("❌ Please check the error messages above and fix the issues")
    
    sys.exit(0 if success else 1)

