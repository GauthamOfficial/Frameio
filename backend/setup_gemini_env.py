#!/usr/bin/env python3
"""
Setup Gemini API Environment
Run this from the backend directory: python setup_gemini_env.py
"""

import os
import sys
from pathlib import Path

def setup_gemini_environment():
    print("🔧 Setting up Gemini API Environment\n")
    
    # Check if .env file exists
    env_file = Path('.env')
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_file.touch()
    
    # Read current .env content
    current_content = ""
    if env_file.exists():
        with open(env_file, 'r') as f:
            current_content = f.read()
    
    # Check if GEMINI_API_KEY is already set
    if 'GEMINI_API_KEY=' in current_content:
        print("⚠️  GEMINI_API_KEY already exists in .env file")
        print("📄 Current .env content:")
        print("-" * 40)
        print(current_content)
        print("-" * 40)
        
        response = input("\nDo you want to update it? (y/n): ")
        if response.lower() != 'y':
            print("✅ Keeping existing configuration")
            return
    
    # Get API key from user
    print("\n🔑 Please enter your Gemini API key:")
    print("   Get it from: https://aistudio.google.com/app/apikey")
    api_key = input("   API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided")
        return
    
    # Update .env file
    print("\n📝 Updating .env file...")
    
    # Remove existing GEMINI_API_KEY line
    lines = current_content.split('\n')
    lines = [line for line in lines if not line.startswith('GEMINI_API_KEY=')]
    
    # Add new GEMINI_API_KEY
    lines.append(f'GEMINI_API_KEY={api_key}')
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write('\n'.join(lines))
    
    print("✅ .env file updated successfully")
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = api_key
    print("✅ Environment variable set for current session")
    
    print("\n🎯 Next steps:")
    print("1. Restart your Django server")
    print("2. Test the AI service with: python diagnose_ai_service.py")
    print("3. Try generating an image in the frontend")

if __name__ == "__main__":
    setup_gemini_environment()





