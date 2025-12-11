"""
Password reset views for handling forgot password functionality.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import secrets
import logging
import os

from .models import PasswordResetToken
from .email_service import send_password_reset_email

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_reset_token():
    """Generate a secure random token for password reset."""
    return secrets.token_urlsafe(32)


@api_view(['POST'])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request password reset - send reset email to user.
    
    Expected payload:
    {
        "email": "user@example.com"
    }
    """
    try:
        email = request.data.get('email', '').strip()
        
        if not email:
            return Response(
                {'error': 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user by email
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            return Response(
                {'message': 'If the email exists, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )
        
        # Generate reset token
        token = generate_reset_token()
        expires_at = timezone.now() + timedelta(hours=1)  # 1 hour expiry
        
        # Create or update reset token (invalidate old unused tokens)
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).update(is_used=True)
        
        # Create new token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at,
            is_used=False
        )
        
        # Build reset URL - redirect to frontend page
        domain_url = settings.DOMAIN_URL or request.build_absolute_uri('/')[:-1]
        # Frontend URL for reset page
        frontend_url = os.getenv('NEXT_PUBLIC_APP_URL', domain_url.replace('/api', ''))
        reset_link = f"{frontend_url}/reset-password?token={token}"
        
        # Send reset email
        email_sent = send_password_reset_email(user, reset_link)
        
        if email_sent:
            logger.info(f"Password reset email sent successfully to {user.email}")
            return Response(
                {'message': 'If the email exists, a password reset link has been sent.'},
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Password reset email could not be sent to {user.email}")
            return Response(
                {'error': 'Failed to send password reset email. Please try again later.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in request_password_reset: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred. Please try again later.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_reset_token(request, token):
    """
    Verify if a password reset token is valid.
    
    GET /api/users/auth/verify-reset-token/{token}/
    """
    try:
        # Get reset token
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is used
        if reset_token.is_used:
            return Response(
                {'error': 'This reset token has already been used.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is expired
        if reset_token.is_expired:
            return Response(
                {'error': 'Reset token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Token is valid
        return Response(
            {
                'message': 'Token is valid',
                'email': reset_token.user.email
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in verify_reset_token: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred while verifying the token.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, token):
    """
    Reset password using a valid reset token.
    
    Expected payload:
    {
        "password": "newpassword123",
        "confirm_password": "newpassword123"
    }
    """
    try:
        password = request.data.get('password', '')
        confirm_password = request.data.get('confirm_password', '')
        
        if not password:
            return Response(
                {'error': 'Password is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if password != confirm_password:
            return Response(
                {'error': 'Passwords do not match'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get reset token
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired reset token.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is used
        if reset_token.is_used:
            return Response(
                {'error': 'This reset token has already been used.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if token is expired
        if reset_token.is_expired:
            return Response(
                {'error': 'Reset token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = reset_token.user
        
        # Validate password
        try:
            validate_password(password, user=user)
        except ValidationError as e:
            error_messages = list(e.messages)
            logger.warning(f"Password validation failed for reset: {error_messages}")
            return Response(
                {'error': 'Password validation failed', 'details': error_messages},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(password)
        user.save()
        
        # Mark token as used
        reset_token.mark_as_used()
        
        # Invalidate all other unused reset tokens for this user
        PasswordResetToken.objects.filter(
            user=user,
            is_used=False
        ).exclude(id=reset_token.id).update(is_used=True)
        
        logger.info(f"Password reset successful for user {user.email}")
        
        return Response(
            {'message': 'Password has been reset successfully. You can now log in with your new password.'},
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in reset_password: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred while resetting the password.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

