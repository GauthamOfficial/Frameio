"""
Custom exception handler for AI services to ensure all errors return JSON responses
"""
import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse

logger = logging.getLogger(__name__)


def ai_services_exception_handler(exc, context):
    """
    Custom exception handler that ensures all errors return proper JSON responses
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If we got a response from DRF, ensure it has proper content
    if response is not None:
        # Ensure response has error message
        if not hasattr(response, 'data') or not response.data:
            response.data = {
                "success": False,
                "error": str(exc) if hasattr(exc, '__str__') else "Internal server error"
            }
        elif isinstance(response.data, dict) and 'error' not in response.data and 'detail' not in response.data:
            # If response.data exists but doesn't have error/detail, add it
            if 'message' in response.data:
                response.data['error'] = response.data['message']
            else:
                response.data['error'] = str(exc) if hasattr(exc, '__str__') else "Internal server error"
        
        # Ensure success field
        if 'success' not in response.data:
            response.data['success'] = False
        
        # Force content type
        response['Content-Type'] = 'application/json'
        
        logger.error(f"Exception handled: {str(exc)}")
        return response
    
    # If DRF didn't handle it, create our own response
    logger.error(f"Unhandled exception: {str(exc)}")
    import traceback
    logger.error(traceback.format_exc())
    
    try:
        error_message = str(exc) if hasattr(exc, '__str__') else "Internal server error"
        return Response({
            "success": False,
            "error": error_message
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        logger.error(f"Failed to create Response: {str(e)}")
        # Last resort - use JsonResponse
        return JsonResponse({
            "success": False,
            "error": "Internal server error"
        }, status=500)



