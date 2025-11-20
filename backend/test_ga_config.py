#!/usr/bin/env python3
"""
Test script to verify Google Analytics configuration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file (same way Django does)
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / '.env'
load_dotenv(env_path)

print("=" * 60)
print("Google Analytics Configuration Test")
print("=" * 60)

# Check Property ID
property_id = os.getenv('GOOGLE_ANALYTICS_PROPERTY_ID')
print(f"\n1. GOOGLE_ANALYTICS_PROPERTY_ID:")
if property_id:
    print(f"   [OK] Found: {property_id}")
else:
    print("   [ERROR] NOT FOUND")

# Check Credentials JSON
creds_json = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_JSON')
print(f"\n2. GOOGLE_ANALYTICS_CREDENTIALS_JSON:")
if creds_json:
    print(f"   [OK] Found (length: {len(creds_json)} characters)")
    # Try to parse it
    try:
        import json
        # Remove surrounding quotes if present
        if creds_json.startswith("'") and creds_json.endswith("'"):
            creds_json = creds_json[1:-1]
        elif creds_json.startswith('"') and creds_json.endswith('"'):
            creds_json = creds_json[1:-1]
        
        creds_dict = json.loads(creds_json)
        print(f"   [OK] Valid JSON")
        print(f"   - Project ID: {creds_dict.get('project_id', 'N/A')}")
        print(f"   - Client Email: {creds_dict.get('client_email', 'N/A')}")
        print(f"   - Has Private Key: {bool(creds_dict.get('private_key', ''))}")
    except json.JSONDecodeError as e:
        print(f"   [ERROR] Invalid JSON: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"   [WARNING] Error parsing JSON: {str(e)}")
else:
    print("   [ERROR] NOT FOUND")

# Check Credentials Path (alternative)
creds_path = os.getenv('GOOGLE_ANALYTICS_CREDENTIALS_PATH')
print(f"\n3. GOOGLE_ANALYTICS_CREDENTIALS_PATH:")
if creds_path:
    if Path(creds_path).exists():
        print(f"   [OK] Found: {creds_path}")
    else:
        print(f"   [WARNING] Path specified but file not found: {creds_path}")
else:
    print("   [INFO] Not set (using JSON string instead)")

# Test Google Analytics Service
print(f"\n4. Testing Google Analytics Service:")
try:
    from ai_services.google_analytics_service import get_google_analytics_service
    ga_service = get_google_analytics_service()
    
    if ga_service.is_configured():
        print("   [OK] Service is configured and ready")
    else:
        print("   [ERROR] Service is NOT configured")
        print("   Check the errors above")
except Exception as e:
    print(f"   [ERROR] Error initializing service: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)

