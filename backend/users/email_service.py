"""
Email service for sending verification emails using Django's email backend.
"""
from django.core.mail import send_mail, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
import socket

logger = logging.getLogger(__name__)


def send_verification_email(user, verification_link):
    """
    Send email verification email to user.
    
    Args:
        user: User instance
        verification_link: Full URL to verification endpoint with token
    """
    # Check if email is configured
    if not settings.EMAIL_HOST_PASSWORD:
        logger.warning(f"EMAIL_HOST_PASSWORD not set. Email not sent to {user.email}. Using console backend.")
        # In development, log the verification link
        logger.info(f"Verification link for {user.email}: {verification_link}")
        return False
    
    try:
        subject = 'Verify Your Email Address - Frameio'
        user_name = user.get_full_name() or user.username or 'there'
        
        # HTML email content
        html_message = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Verify Your Email</title>
          </head>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
              <h1 style="color: white; margin: 0;">Welcome to Frameio!</h1>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
              <p style="font-size: 16px;">Hi {user_name},</p>
              <p style="font-size: 16px;">Thank you for signing up! Please verify your email address to complete your registration.</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" 
                   style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                  Verify Email Address
                </a>
              </div>
              <p style="font-size: 14px; color: #666;">If the button doesn't work, copy and paste this link into your browser:</p>
              <p style="font-size: 12px; color: #999; word-break: break-all;">{verification_link}</p>
              <p style="font-size: 14px; color: #666; margin-top: 30px;">This link will expire in 24 hours.</p>
              <p style="font-size: 14px; color: #666;">If you didn't create an account, you can safely ignore this email.</p>
            </div>
            <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
              <p>&copy; {settings.DOMAIN_URL or 'Frameio'} {__import__('datetime').datetime.now().year}. All rights reserved.</p>
            </div>
          </body>
        </html>
        """
        
        # Plain text version
        plain_message = f"""
Welcome to Frameio!

Hi {user_name},

Thank you for signing up! Please verify your email address by clicking the link below:

{verification_link}

This link will expire in 24 hours.

If you didn't create an account, you can safely ignore this email.

© {settings.DOMAIN_URL or 'Frameio'} {__import__('datetime').datetime.now().year}. All rights reserved.
        """
        
        # Get connection with timeout settings
        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
            timeout=getattr(settings, 'EMAIL_TIMEOUT', 10),
        )
        
        # Send email with connection
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            connection=connection,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent successfully to {user.email}")
        return True
        
    except socket.timeout as e:
        logger.error(f"SMTP connection timeout when sending verification email to {user.email}: {e}")
        logger.error(f"Check your network connection and firewall settings. SMTP host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        return False
    except socket.error as e:
        logger.error(f"SMTP connection error when sending verification email to {user.email}: {e}")
        logger.error(f"Check your network connection and SMTP settings. Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
        return False
    except Exception as e:
        logger.error(f"Error sending verification email to {user.email}: {e}", exc_info=True)
        logger.error(f"Email configuration - Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}, User: {settings.EMAIL_HOST_USER}")
        return False


def send_password_reset_email(user, reset_link):
    """
    Send password reset email to user.
    
    Args:
        user: User instance
        reset_link: Full URL to password reset endpoint with token
    """
    try:
        subject = 'Reset Your Password - Frameio'
        user_name = user.get_full_name() or user.username or 'there'
        
        html_message = f"""
        <!DOCTYPE html>
        <html>
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Password</title>
          </head>
          <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
              <h1 style="color: white; margin: 0;">Password Reset Request</h1>
            </div>
            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #e0e0e0;">
              <p style="font-size: 16px;">Hi {user_name},</p>
              <p style="font-size: 16px;">You requested to reset your password. Click the button below to create a new password.</p>
              <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" 
                   style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                  Reset Password
                </a>
              </div>
              <p style="font-size: 14px; color: #666;">If the button doesn't work, copy and paste this link into your browser:</p>
              <p style="font-size: 12px; color: #999; word-break: break-all;">{reset_link}</p>
              <p style="font-size: 14px; color: #666; margin-top: 30px;">This link will expire in 1 hour.</p>
              <p style="font-size: 14px; color: #666;">If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div style="text-align: center; margin-top: 20px; color: #999; font-size: 12px;">
              <p>&copy; {settings.DOMAIN_URL or 'Frameio'} {__import__('datetime').datetime.now().year}. All rights reserved.</p>
            </div>
          </body>
        </html>
        """
        
        plain_message = f"""
Password Reset Request

Hi {user_name},

You requested to reset your password. Click the link below to create a new password:

{reset_link}

This link will expire in 1 hour.

If you didn't request a password reset, you can safely ignore this email.

© {settings.DOMAIN_URL or 'Frameio'} {__import__('datetime').datetime.now().year}. All rights reserved.
        """
        
        # Get connection with timeout settings
        connection = get_connection(
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=settings.EMAIL_HOST_PASSWORD,
            use_tls=settings.EMAIL_USE_TLS,
            use_ssl=getattr(settings, 'EMAIL_USE_SSL', False),
            timeout=getattr(settings, 'EMAIL_TIMEOUT', 10),
        )
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            connection=connection,
            fail_silently=False,
        )
        
        logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except socket.timeout as e:
        logger.error(f"SMTP connection timeout when sending password reset email to {user.email}: {e}")
        return False
    except socket.error as e:
        logger.error(f"SMTP connection error when sending password reset email to {user.email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Error sending password reset email to {user.email}: {e}", exc_info=True)
        return False

