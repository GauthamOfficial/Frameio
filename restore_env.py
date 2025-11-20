#!/usr/bin/env python3
"""
Environment File Restoration Script for Frameio Project
This script helps restore the .env file from the template
"""

import os
import shutil
from pathlib import Path

def restore_env_file():
    """Restore the .env file from the template"""
    
    # Check if .env already exists
    env_file = Path('.env')
    template_file = Path('env.template')
    
    if env_file.exists():
        print("⚠️  .env file already exists!")
        response = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if response != 'y':
            print("❌ Operation cancelled.")
            return False
    
    if not template_file.exists():
        print("❌ Template file 'env.template' not found!")
        return False
    
    try:
        # Copy template to .env
        shutil.copy2(template_file, env_file)
        print("✅ .env file restored successfully!")
        print(f"📁 Created: {env_file.absolute()}")
        
        # Show next steps
        print("\n📋 Next Steps:")
        print("1. Edit the .env file with your actual API keys")
        print("2. Update database credentials if needed")
        print("3. Configure Clerk authentication keys")
        print("4. Set up AI service API keys (NanoBanana, etc.)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error restoring .env file: {e}")
        return False

def show_env_status():
    """Show current environment status"""
    
    print("🔍 Environment Status Check:")
    print("=" * 50)
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env file exists")
        
        # Check for required variables
        required_vars = [
            'SECRET_KEY',
            'DEBUG', 
            'DB_NAME',
            'CLERK_PUBLISHABLE_KEY',
            'CLERK_SECRET_KEY'
        ]
        
        missing_vars = []
        with open(env_file, 'r') as f:
            content = f.read()
            for var in required_vars:
                if f"{var}=" not in content:
                    missing_vars.append(var)
        
        if missing_vars:
            print(f"⚠️  Missing variables: {', '.join(missing_vars)}")
        else:
            print("✅ All required variables present")
            
    else:
        print("❌ .env file not found")
    
    print("\n📁 Template file:", "✅ exists" if Path('env.template').exists() else "❌ missing")

def main():
    """Main function"""
    print("🚀 Frameio Environment File Restoration")
    print("=" * 50)
    
    # Show current status
    show_env_status()
    
    print("\n" + "=" * 50)
    print("Options:")
    print("1. Restore .env file from template")
    print("2. Show environment status only")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        restore_env_file()
    elif choice == '2':
        show_env_status()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice!")

if __name__ == "__main__":
    main()
