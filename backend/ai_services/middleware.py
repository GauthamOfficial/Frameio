"""
Arcjet middleware for AI services rate limiting and security
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from organizations.middleware import get_current_organization

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware for AI API endpoints
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Store rate limit data in memory (in production, use Redis)
        self.rate_limits = defaultdict(lambda: defaultdict(deque))
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process incoming request for rate limiting"""
        
        # Only apply to AI service endpoints
        if not request.path.startswith('/api/ai/'):
            return None
        
        # Get organization and user identifiers
        organization = get_current_organization()
        if not organization:
            return JsonResponse(
                {'error': 'Organization context required'}, 
                status=400
            )
        
        user_id = str(request.user.id) if request.user.is_authenticated else 'anonymous'
        org_id = str(organization.id)
        
        # Define rate limits based on endpoint
        rate_limits = self._get_rate_limits(request.path, request.method)
        
        # Check rate limits
        for limit_type, (limit, window_seconds) in rate_limits.items():
            key = f"{org_id}:{user_id}:{limit_type}"
            
            if self._is_rate_limited(key, limit, window_seconds):
                return JsonResponse(
                    {
                        'error': f'Rate limit exceeded for {limit_type}',
                        'limit': limit,
                        'window_seconds': window_seconds,
                        'retry_after': self._get_retry_after(key, window_seconds)
                    },
                    status=429
                )
        
        # Record the request
        self._record_request(org_id, user_id, request.path)
        
        return None
    
    def _get_rate_limits(self, path, method):
        """Get rate limits for specific endpoint"""
        limits = {}
        
        if '/ai/generation-requests/' in path and method == 'POST':
            # AI generation requests - more restrictive
            limits['ai_generation'] = (10, 60)  # 10 requests per minute
            limits['ai_generation_hourly'] = (100, 3600)  # 100 requests per hour
        
        elif '/ai/generation-requests/' in path and method == 'GET':
            # Viewing requests - less restrictive
            limits['api_read'] = (100, 60)  # 100 requests per minute
        
        elif '/ai/templates/' in path and method == 'POST':
            # Template usage
            limits['template_usage'] = (20, 60)  # 20 requests per minute
        
        else:
            # Default limits for other AI endpoints
            limits['api_general'] = (60, 60)  # 60 requests per minute
        
        return limits
    
    def _is_rate_limited(self, key, limit, window_seconds):
        """Check if request should be rate limited"""
        now = time.time()
        window_start = now - window_seconds
        
        # Clean old entries
        request_times = self.rate_limits[key]['requests']
        while request_times and request_times[0] < window_start:
            request_times.popleft()
        
        # Check if limit exceeded
        return len(request_times) >= limit
    
    def _record_request(self, org_id, user_id, path):
        """Record a request for rate limiting"""
        now = time.time()
        
        # Record for different rate limit types
        rate_limit_keys = [
            f"{org_id}:{user_id}:ai_generation",
            f"{org_id}:{user_id}:ai_generation_hourly",
            f"{org_id}:{user_id}:api_read",
            f"{org_id}:{user_id}:template_usage",
            f"{org_id}:{user_id}:api_general"
        ]
        
        for key in rate_limit_keys:
            self.rate_limits[key]['requests'].append(now)
    
    def _get_retry_after(self, key, window_seconds):
        """Get retry after time in seconds"""
        request_times = self.rate_limits[key]['requests']
        if request_times:
            oldest_request = request_times[0]
            return max(0, int(oldest_request + window_seconds - time.time()))
        return 0


class AISecurityMiddleware(MiddlewareMixin):
    """
    Security middleware for AI services
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Suspicious patterns to detect
        self.suspicious_patterns = [
            'jailbreak', 'ignore previous', 'system prompt', 'admin override',
            'bypass', 'hack', 'exploit', 'injection', 'malicious'
        ]
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request for security checks"""
        
        # Only apply to AI generation endpoints
        if not (request.path.startswith('/api/ai/generation-requests/') and 
                request.method == 'POST'):
            return None
        
        # Check request body for suspicious content
        if hasattr(request, 'data') and isinstance(request.data, dict):
            prompt = request.data.get('prompt', '')
            
            if self._contains_suspicious_content(prompt):
                logger.warning(
                    f"Suspicious AI prompt detected from user {request.user.id}: {prompt[:100]}..."
                )
                return JsonResponse(
                    {
                        'error': 'Request contains potentially harmful content',
                        'code': 'CONTENT_POLICY_VIOLATION'
                    },
                    status=400
                )
        
        return None
    
    def _contains_suspicious_content(self, text):
        """Check if text contains suspicious patterns"""
        if not text:
            return False
        
        text_lower = text.lower()
        
        # Check for suspicious patterns
        for pattern in self.suspicious_patterns:
            if pattern in text_lower:
                return True
        
        # Check for excessive length (potential DoS)
        if len(text) > 5000:  # 5000 character limit
            return True
        
        # Check for repeated characters (potential spam)
        if self._has_excessive_repetition(text):
            return True
        
        return False
    
    def _has_excessive_repetition(self, text):
        """Check for excessive character repetition"""
        if len(text) < 10:
            return False
        
        # Check for same character repeated more than 20 times
        for i in range(len(text) - 20):
            if len(set(text[i:i+20])) == 1:
                return True
        
        return False


class AIUsageTrackingMiddleware(MiddlewareMixin):
    """
    Middleware to track AI usage for analytics
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """Track AI API usage"""
        
        # Only track AI service endpoints
        if not request.path.startswith('/api/ai/'):
            return None
        
        # Store request start time
        request._ai_start_time = time.time()
        
        return None
    
    def process_response(self, request, response):
        """Log AI API usage after response"""
        
        if not hasattr(request, '_ai_start_time'):
            return response
        
        # Calculate response time
        response_time = time.time() - request._ai_start_time
        
        # Log usage
        organization = get_current_organization()
        org_name = organization.name if organization else 'unknown'
        
        logger.info(
            f"AI API Usage - Org: {org_name}, "
            f"User: {request.user.id if request.user.is_authenticated else 'anonymous'}, "
            f"Path: {request.path}, Method: {request.method}, "
            f"Status: {response.status_code}, Time: {response_time:.3f}s"
        )
        
        return response
