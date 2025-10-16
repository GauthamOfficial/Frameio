#!/usr/bin/env python3
"""
Run Simple Branding Test
Test the simplified branding approach that includes all branding information in the prompt.
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

from test_simple_branding import main

if __name__ == "__main__":
    print("🚀 Running Simple Branding Test...")
    print("This will test the simplified branding approach that includes all branding information in the prompt.")
    print("=" * 80)
    
    success = main()
    
    if success:
        print("\n🎉 SUCCESS! Simple branding approach is working correctly!")
        print("✅ Company logos and contact details are integrated into AI generation")
        print("✅ No complex logo handling needed - everything in the prompt")
        print("✅ AI naturally incorporates branding into the poster design")
    else:
        print("\n❌ FAILED! Simple branding approach is not working correctly")
        print("❌ Please check the error messages above and fix the issues")
    
    sys.exit(0 if success else 1)
