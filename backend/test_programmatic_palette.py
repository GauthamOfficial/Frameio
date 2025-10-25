#!/usr/bin/env python3
"""
Test programmatic color palette generation
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from ai_services.branding_kit_service import BrandingKitService

def test_programmatic_palette():
    """Test programmatic color palette generation"""
    service = BrandingKitService()
    
    # Test cases with specific colors
    test_cases = [
        {
            "prompt": "Create a brand with blue and green colors",
            "expected_colors": ["blue", "green"]
        },
        {
            "prompt": "Modern tech startup with purple theme",
            "expected_colors": ["purple"]
        },
        {
            "prompt": "Elegant brand using navy and gold",
            "expected_colors": ["navy", "gold"]
        },
        {
            "prompt": "Fashion brand with pink and white",
            "expected_colors": ["pink", "white"]
        }
    ]
    
    print("Testing programmatic color palette generation...")
    
    for i, test_case in enumerate(test_cases, 1):
        prompt = test_case["prompt"]
        expected = test_case["expected_colors"]
        
        print(f"\n--- Test {i}: {prompt} ---")
        print(f"Expected colors: {expected}")
        
        try:
            result = service.generate_color_palette(prompt, 5)
            
            if result.get('success'):
                print("✅ Color palette generated successfully!")
                print(f"   Used colors: {result.get('used_colors', [])}")
                print(f"   Generation method: {result.get('generation_method', 'unknown')}")
                print(f"   Instructions: {result.get('instructions', 'N/A')}")
                
                # Check if the used colors match expected
                used_colors = result.get('used_colors', [])
                if set(used_colors) == set(expected):
                    print("✅ Colors match expected!")
                else:
                    print("❌ Colors don't match expected!")
                    print(f"   Expected: {expected}")
                    print(f"   Got: {used_colors}")
            else:
                print(f"❌ Color palette generation failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_programmatic_palette()
