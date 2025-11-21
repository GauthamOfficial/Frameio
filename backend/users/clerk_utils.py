"""
Utility functions for Clerk user synchronization with Django.
"""
from django.contrib.auth import get_user_model
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


def get_or_create_user_from_clerk(
    clerk_id=None,
    email=None,
    first_name=None,
    last_name=None,
    username=None,
    image_url=None,
    verified=None
):
    """
    Get or create a Django user from Clerk user data.
    
    Args:
        clerk_id: Clerk user ID
        email: User email address (required)
        first_name: User's first name
        last_name: User's last name
        username: Username (if not provided, derived from email)
        image_url: User's profile image URL
        verified: Whether the email is verified
    
    Returns:
        tuple: (user, created) - Django user object and boolean indicating if created
    """
    if not email:
        logger.error("get_or_create_user_from_clerk: email is required")
        return None, False
    
    # Try to find existing user by email or clerk_id
    user = None
    if clerk_id:
        user = User.objects.filter(clerk_id=clerk_id).first()
    
    if not user:
        user = User.objects.filter(email=email).first()
    
    if user:
        # Update existing user with latest Clerk data
        updated = False
        if clerk_id and user.clerk_id != clerk_id:
            user.clerk_id = clerk_id
            updated = True
        
        if first_name and user.first_name != first_name:
            user.first_name = first_name
            updated = True
        
        if last_name and user.last_name != last_name:
            user.last_name = last_name
            updated = True
        
        if verified is not None and user.is_verified != verified:
            user.is_verified = verified
            updated = True
        
        if updated:
            user.save()
            logger.info(f"Updated user {user.email} with Clerk data")
        
        return user, False
    
    # Create new user
    # Generate username from email if not provided
    if not username:
        username = email.split('@')[0]
    
    # Make username unique
    base_username = username
    counter = 1
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=None,  # No password for Clerk-authenticated users
            first_name=first_name or '',
            last_name=last_name or '',
            clerk_id=clerk_id,
            is_active=True,
            is_verified=verified if verified is not None else True,
        )
        
        # Set password to unusable
        user.set_unusable_password()
        user.save()
        
        logger.info(f"Created new user from Clerk: {user.email} (clerk_id: {clerk_id})")
        return user, True
        
    except Exception as e:
        logger.error(f"Error creating user from Clerk data: {e}", exc_info=True)
        raise


def get_or_create_user_from_email(email, first_name=None, last_name=None):
    """
    Simplified function to get or create user from email only.
    Used when full Clerk data is not available.
    """
    return get_or_create_user_from_clerk(
        email=email,
        first_name=first_name,
        last_name=last_name
    )

