#!/usr/bin/env python
"""
Generate a new Django secret key for the .env file.
Run this script to generate a secure secret key for your environment.
"""

import os
import sys
import django
from django.core.management.utils import get_random_secret_key

def main():
    """Generate and display a new Django secret key."""
    print("=" * 60)
    print("Django Secret Key Generator")
    print("=" * 60)
    print()
    
    # Generate a new secret key
    secret_key = get_random_secret_key()
    
    print("Generated Secret Key:")
    print("-" * 40)
    print(secret_key)
    print("-" * 40)
    print()
    
    print("Instructions:")
    print("1. Copy the secret key above")
    print("2. Paste it into your .env file as the SECRET_KEY value")
    print("3. Make sure to keep this key secure and never commit it to version control")
    print()
    
    # Check if .env file exists
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        print(f"Note: .env file found at {env_file}")
        print("You can update the SECRET_KEY value in that file.")
    else:
        print("Note: No .env file found. Create one using env.template as a starting point.")
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    main()






