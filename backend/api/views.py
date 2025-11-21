from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.conf import settings
import os
import uuid

@api_view(['POST'])
def textile_poster(request):
    """
    POST /api/textile/poster/
    Body: { "product_name": "Silk Saree", "offer_details": "25% OFF Festive Sale" }
    """
    return Response({
        "success": False,
        "error": "AI image generation has been disabled"
    }, status=503)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def two_step_generation_test(request):
    """
    POST /api/test/two-step/
    AI image generation has been disabled
    """
    return Response({
        "success": False,
        "error": "AI image generation has been disabled"
    }, status=503)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_file(request):
    """
    POST /api/upload/
    Handle single file upload
    """
    if 'file' not in request.FILES:
        return Response({
            "success": False,
            "error": "No file provided"
        }, status=400)
    
    file = request.FILES['file']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        return Response({
            "success": False,
            "error": f"File type {file.content_type} not supported. Allowed types: {', '.join(allowed_types)}"
        }, status=400)
    
    # Validate file size (10MB max)
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        return Response({
            "success": False,
            "error": f"File too large. Maximum size is {max_size // (1024 * 1024)}MB"
        }, status=400)
    
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Save file
        file_path = default_storage.save(f"uploads/{unique_filename}", ContentFile(file.read()))
        file_url = request.build_absolute_uri(default_storage.url(file_path))
        
        return Response({
            "success": True,
            "url": file_url,
            "filename": unique_filename,
            "original_name": file.name,
            "size": file.size,
            "content_type": file.content_type,
            "uploaded_at": file.name  # Placeholder for timestamp
        })
        
    except Exception as e:
        return Response({
            "success": False,
            "error": f"Upload failed: {str(e)}"
        }, status=500)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def upload_multiple_files(request):
    """
    POST /api/upload/multiple/
    Handle multiple file upload
    """
    if 'files' not in request.FILES:
        return Response({
            "success": False,
            "error": "No files provided"
        }, status=400)
    
    files = request.FILES.getlist('files')
    uploaded_files = []
    errors = []
    
    for i, file in enumerate(files):
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if file.content_type not in allowed_types:
            errors.append(f"File {i+1} ({file.name}): Invalid file type")
            continue
        
        # Validate file size (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            errors.append(f"File {i+1} ({file.name}): File too large")
            continue
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Save file
            file_path = default_storage.save(f"uploads/{unique_filename}", ContentFile(file.read()))
            file_url = request.build_absolute_uri(default_storage.url(file_path))
            
            uploaded_files.append({
                "url": file_url,
                "filename": unique_filename,
                "original_name": file.name,
                "size": file.size,
                "content_type": file.content_type,
                "uploaded_at": file.name  # Placeholder for timestamp
            })
            
        except Exception as e:
            errors.append(f"File {i+1} ({file.name}): {str(e)}")
    
    return Response({
        "success": True,
        "uploaded_files": uploaded_files,
        "errors": errors
    })

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def generate_social_media_post(request):
    """
    POST /api/ai/post-generation/generate_social_media_post/
    AI image generation has been disabled
    """
    return Response({
        "success": False,
        "error": "AI image generation has been disabled"
    }, status=503)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def contact_form(request):
    """
    POST /api/contact/
    Handle contact form submissions and send email
    Body: { "name": "John Doe", "email": "john@example.com", "message": "Hello..." }
    """
    try:
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip()
        message = request.data.get('message', '').strip()
        
        # Validation
        if not name:
            return Response({
                "success": False,
                "error": "Name is required"
            }, status=400)
        
        if not email:
            return Response({
                "success": False,
                "error": "Email is required"
            }, status=400)
        
        if not message or len(message) < 10:
            return Response({
                "success": False,
                "error": "Message must be at least 10 characters long"
            }, status=400)
        
        # Email validation
        import re
        if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
            return Response({
                "success": False,
                "error": "Please enter a valid email address"
            }, status=400)
        
        # Send email
        subject = f"New Contact Form Submission from {name}"
        email_message = f"""
You have received a new message from the Frameio contact form:

Name: {name}
Email: {email}

Message:
{message}

---
This message was sent from the Frameio contact form.
"""
        
        recipient_email = 'startuptsg@gmail.com'
        
        try:
            send_mail(
                subject,
                email_message,
                settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL,
                [recipient_email],
                fail_silently=False,
            )
            
            return Response({
                "success": True,
                "message": "Thank you for contacting us. We'll get back to you soon."
            })
            
        except Exception as e:
            # Log the error but don't expose it to the user
            print(f"Error sending email: {str(e)}")
            return Response({
                "success": False,
                "error": "Failed to send message. Please try again later."
            }, status=500)
            
    except Exception as e:
        return Response({
            "success": False,
            "error": f"An error occurred: {str(e)}"
        }, status=500)