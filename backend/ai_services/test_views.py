"""
Test views for Phase 1 Week 3 functionality
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json


def test_interface(request):
    """Serve the test interface for Phase 1 Week 3"""
    return render(request, 'ai_services/test_interface.html')


@csrf_exempt
def test_poster_generation(request):
    """Test endpoint for poster generation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Mock response for testing
            response_data = {
                'success': True,
                'poster_url': 'https://example.com/generated_poster.jpg',
                'caption': f"Beautiful {data.get('fabric_type', 'textile')} for {data.get('festival', 'special occasions')}",
                'hashtags': ['#textile', '#fashion', '#festival', '#style'],
                'message': 'Poster generated successfully (mock response)'
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def test_caption_generation(request):
    """Test endpoint for caption generation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Mock response for testing
            response_data = {
                'success': True,
                'captions': [
                    f"Stunning {data.get('product_name', 'textile product')} perfect for {data.get('festival', 'any occasion')}",
                    f"Elegant {data.get('fabric_type', 'fabric')} design that speaks volumes",
                    f"Make a statement with this beautiful {data.get('style', 'elegant')} piece"
                ],
                'hashtags': ['#textile', '#fashion', '#elegant', '#style', '#festival'],
                'message': 'Captions generated successfully (mock response)'
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def test_schedule_creation(request):
    """Test endpoint for schedule creation"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Mock response for testing
            response_data = {
                'success': True,
                'scheduled_post_id': 123,
                'platform': data.get('platform', 'facebook'),
                'scheduled_time': data.get('scheduled_time'),
                'status': 'scheduled',
                'message': 'Post scheduled successfully (mock response)'
            }
            return JsonResponse(response_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


def test_analytics(request):
    """Test endpoint for analytics"""
    if request.method == 'GET':
        # Mock response for testing
        response_data = {
            'success': True,
            'total_posts': 25,
            'scheduled_posts': 10,
            'posted_posts': 12,
            'failed_posts': 3,
            'platforms': {
                'facebook': 8,
                'instagram': 7,
                'tiktok': 5,
                'whatsapp': 3,
                'twitter': 2
            },
            'message': 'Analytics retrieved successfully (mock response)'
        }
        return JsonResponse(response_data)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)
