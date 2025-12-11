"""
Script to manually verify a user's email for testing purposes.
Usage: python manage.py shell < manually_verify_user.py
Or: python manage.py shell -c "exec(open('manually_verify_user.py').read())"
"""
from users.models import User

# Replace with the email you want to verify
email_to_verify = 'kumargauthams287@gmail.com'

try:
    user = User.objects.get(email=email_to_verify)
    print(f"Found user: {user.email}")
    print(f"Current is_verified status: {user.is_verified}")
    
    # Verify the user
    user.is_verified = True
    user.save(update_fields=['is_verified'])
    
    # Refresh to confirm
    user.refresh_from_db()
    
    print(f"Updated is_verified status: {user.is_verified}")
    print(f"✅ User {user.email} has been manually verified!")
    
except User.DoesNotExist:
    print(f"❌ User with email {email_to_verify} not found")
except Exception as e:
    print(f"❌ Error: {e}")


