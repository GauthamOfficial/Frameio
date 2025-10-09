#!/usr/bin/env python3
"""
Setup Gemini API Quickstart
Configures the environment and tests the Gemini API integration
"""
import os
import sys
import subprocess

def install_requirements():
    """Install the required packages"""
    print("📦 Installing Google GenAI SDK...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-U", "google-genai"])
        print("✅ Google GenAI SDK installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Google GenAI SDK: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment variables...")
    
    # The API key you provided
    api_key = "AIzaSyDtjWMwLhP4nZIv5LeShDX_cqIQ9y2Rhuc"
    
    # Set environment variable for this session
    os.environ['GEMINI_API_KEY'] = api_key
    os.environ['GOOGLE_API_KEY'] = api_key
    
    print(f"✅ API key set: {api_key[:10]}...")
    
    # Check if .env file exists and update it
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        print("📝 Updating .env file...")
        with open(env_file, 'r') as f:
            content = f.read()
        
        # Update or add GEMINI_API_KEY
        if 'GEMINI_API_KEY=' in content:
            # Replace existing
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('GEMINI_API_KEY='):
                    lines[i] = f'GEMINI_API_KEY={api_key}'
                    break
            content = '\n'.join(lines)
        else:
            # Add new line
            content += f'\nGEMINI_API_KEY={api_key}\n'
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        print("✅ .env file updated")
    else:
        print("ℹ️ .env file not found, using environment variables only")
    
    return True

def test_gemini_integration():
    """Test the Gemini integration"""
    print("🧪 Testing Gemini integration...")
    
    try:
        # Import and test
        from google import genai
        from google.genai import types
        
        # Initialize client
        client = genai.Client(api_key=os.environ['GEMINI_API_KEY'])
        
        # Test basic generation
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents="Hello, Gemini! Are you working?"
        )
        
        print(f"✅ Gemini response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Gemini API Quickstart")
    print("=" * 50)
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Setup environment
    if not setup_environment():
        return False
    
    # Step 3: Test integration
    if not test_gemini_integration():
        return False
    
    print("\n🎉 Gemini API Quickstart setup completed successfully!")
    print("\nNext steps:")
    print("1. Run: python backend/gemini_quickstart_test.py")
    print("2. Check the existing Gemini services in your project")
    print("3. Use the API key in your applications")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
