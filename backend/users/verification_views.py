"""
Email verification views for user account verification.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
import secrets
import logging
import os

from .models import EmailVerificationToken
from .email_service import send_verification_email
from .serializers import UserSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


def generate_verification_token():
    """Generate a secure random token for email verification."""
    return secrets.token_urlsafe(32)


@api_view(['POST'])
@permission_classes([AllowAny])
def send_verification_email_view(request):
    """
    Send verification email to user.
    
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
                {'message': 'If the email exists, a verification link has been sent.'},
                status=status.HTTP_200_OK
            )
        
        # Check if already verified
        if user.is_verified:
            return Response(
                {'message': 'Email is already verified'},
                status=status.HTTP_200_OK
            )
        
        # Generate verification token
        token = generate_verification_token()
        expires_at = timezone.now() + timedelta(hours=24)
        
        # Create or update verification token
        verification_token, created = EmailVerificationToken.objects.update_or_create(
            user=user,
            is_used=False,
            defaults={
                'token': token,
                'expires_at': expires_at,
                'is_used': False,
            }
        )
        
        # Build verification URL - redirect to frontend page
        domain_url = settings.DOMAIN_URL or request.build_absolute_uri('/')[:-1]
        # Frontend URL for verification page
        frontend_url = os.getenv('NEXT_PUBLIC_APP_URL', domain_url.replace('/api', ''))
        verification_link = f"{frontend_url}/check-email?token={token}"
        
        # Send verification email
        email_sent = send_verification_email(user, verification_link)
        
        if email_sent:
            logger.info(f"Verification email sent to {user.email}")
            return Response(
                {'message': 'Verification email sent successfully'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': 'Failed to send verification email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error sending verification email: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred while sending verification email'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_email(request, token):
    """
    Verify user email with token.
    
    GET /api/users/auth/verify-email/{token}/
    POST /api/users/auth/verify-email/{token}/
    """
    try:
        # Get verification token (check both used and unused tokens)
        try:
            verification_token = EmailVerificationToken.objects.get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid or expired verification token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = verification_token.user
        
        # If token is already used, check if user is already verified
        if verification_token.is_used:
            if user.is_verified:
                # User is already verified, just log them in
                logger.info(f"Token already used but user {user.email} is verified, logging in")
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                refresh_token = str(refresh)
                user_serializer = UserSerializer(user)
                
                return Response(
                    {
                        'message': 'Email already verified. Logging you in...',
                        'user': user_serializer.data,
                        'access': access_token,
                        'refresh': refresh_token,
                        'already_verified': True
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Token used but user not verified - might be a race condition
                # Try to verify again
                user.is_verified = True
                user.save(update_fields=['is_verified'])
                logger.info(f"Token was used but user {user.email} wasn't verified, verifying now")
        
        # Check if token is expired (only for unused tokens)
        if not verification_token.is_used and verification_token.is_expired:
            return Response(
                {'error': 'Verification token has expired. Please request a new one.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify user email (if not already verified)
        if not user.is_verified:
            user.is_verified = True
            user.save(update_fields=['is_verified'])
            # Force database commit by refreshing from database
            user.refresh_from_db()
            logger.info(f"Email verified for user {user.email} - is_verified: {user.is_verified}")
        
        # Mark token as used (if not already used)
        if not verification_token.is_used:
            verification_token.mark_as_used()
        
        # Double-check that user is verified before generating tokens
        if not user.is_verified:
            logger.error(f"User {user.email} verification failed - is_verified still False after save")
            return Response(
                {'error': 'Verification failed. Please try again or contact support.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Generate JWT tokens for automatic login
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Serialize user data
        user_serializer = UserSerializer(user)
        
        return Response(
            {
                'message': 'Email verified successfully',
                'user': user_serializer.data,
                'access': access_token,
                'refresh': refresh_token,
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error verifying email: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred while verifying email'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_verification_status(request):
    """
    Check if current user's email is verified.
    
    GET /api/users/auth/verification-status/
    """
    try:
        user = request.user
        return Response(
            {
                'is_verified': user.is_verified,
                'email': user.email,
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Error checking verification status: {e}", exc_info=True)
        return Response(
            {'error': 'An error occurred while checking verification status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

