"""
Test script to verify email configuration
Run this from the backend directory: python test_email_config.py
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to the path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'frameio_backend.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def test_email_config():
    """Test email configuration"""
    print("=" * 60)
    print("Testing Email Configuration")
    print("=" * 60)
    
    # Check configuration
    print(f"\nEmail Backend: {settings.EMAIL_BACKEND}")
    print(f"Email Host: {settings.EMAIL_HOST}")
    print(f"Email Port: {settings.EMAIL_PORT}")
    print(f"Email Use TLS: {settings.EMAIL_USE_TLS}")
    print(f"Email Host User: {settings.EMAIL_HOST_USER}")
    print(f"Email Host Password: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")
    
    # Check if password is set
    if not settings.EMAIL_HOST_PASSWORD:
        print("\n⚠️  WARNING: EMAIL_HOST_PASSWORD is not set!")
        print("   Emails will be printed to console (console backend)")
        print("   To send real emails, set EMAIL_HOST_PASSWORD in your .env file")
        return False
    
    # Test sending email
    print("\n" + "=" * 60)
    print("Attempting to send test email...")
    print("=" * 60)
    
    try:
        send_mail(
            subject='Test Email from Frameio',
            message='This is a test email to verify email configuration is working correctly.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['startuptsg@gmail.com'],
            fail_silently=False,
        )
        print("\n✅ SUCCESS: Test email sent successfully!")
        print("   Check startuptsg@gmail.com inbox for the test email.")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to send email")
        print(f"   Error: {str(e)}")
        print("\nCommon issues:")
        print("1. EMAIL_HOST_PASSWORD might be incorrect")
        print("2. For Gmail, you need to use an App Password (not your regular password)")
        print("3. Check if 'Less secure app access' is enabled (older Gmail accounts)")
        print("4. Verify EMAIL_HOST, EMAIL_PORT, and EMAIL_USE_TLS settings")
        return False

if __name__ == '__main__':
    test_email_config()

