"""
Google Analytics API Views for Admin Dashboard
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
import logging

from ai_services.google_analytics_service import get_google_analytics_service
from users.permissions import IsAuthenticatedOrAdmin

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_overview(request):
    """
    GET /api/admin/analytics/overview
    Get Google Analytics overview statistics
    """
    try:
        days = int(request.GET.get('days', 30))
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False,
                'message': 'Please configure GOOGLE_ANALYTICS_PROPERTY_ID and credentials'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        overview = ga_service.get_overview_stats(days=days)
        
        return Response({
            'configured': True,
            'data': overview
        })
        
    except Exception as e:
        logger.error(f"Error fetching Google Analytics overview: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_user_growth(request):
    """
    GET /api/admin/analytics/user-growth
    Get user growth data over time
    """
    try:
        days = int(request.GET.get('days', 180))
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        data = ga_service.get_user_growth_data(days=days)
        
        return Response({
            'configured': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching user growth data: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_device_breakdown(request):
    """
    GET /api/admin/analytics/device-breakdown
    Get device breakdown statistics
    """
    try:
        days = int(request.GET.get('days', 30))
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        data = ga_service.get_device_breakdown(days=days)
        
        return Response({
            'configured': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching device breakdown: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_top_pages(request):
    """
    GET /api/admin/analytics/top-pages
    Get top pages by page views
    """
    try:
        days = int(request.GET.get('days', 30))
        limit = int(request.GET.get('limit', 10))
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        data = ga_service.get_top_pages(days=days, limit=limit)
        
        return Response({
            'configured': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching top pages: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_traffic_sources(request):
    """
    GET /api/admin/analytics/traffic-sources
    Get traffic sources breakdown
    """
    try:
        days = int(request.GET.get('days', 30))
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        data = ga_service.get_traffic_sources(days=days)
        
        return Response({
            'configured': True,
            'data': data
        })
        
    except Exception as e:
        logger.error(f"Error fetching traffic sources: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticatedOrAdmin])
def google_analytics_all(request):
    """
    GET /api/admin/analytics
    Get all Google Analytics data in one request
    """
    try:
        days = int(request.GET.get('days', 30))
        time_range = request.GET.get('timeRange', '30d')
        
        # Map time range to days
        time_range_map = {
            '7d': 7,
            '30d': 30,
            '90d': 90,
            '1y': 365
        }
        days = time_range_map.get(time_range, days)
        
        ga_service = get_google_analytics_service()
        
        if not ga_service.is_configured():
            return Response({
                'error': 'Google Analytics not configured',
                'configured': False,
                'message': 'Please configure GOOGLE_ANALYTICS_PROPERTY_ID and credentials'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Fetch all data
        overview = ga_service.get_overview_stats(days=days)
        user_growth = ga_service.get_user_growth_data(days=min(days * 6, 180))  # 6 months max for growth
        device_breakdown = ga_service.get_device_breakdown(days=days)
        top_pages = ga_service.get_top_pages(days=days, limit=10)
        traffic_sources = ga_service.get_traffic_sources(days=days)
        
        return Response({
            'configured': True,
            'data': {
                'overview': overview,
                'userGrowth': user_growth,
                'deviceBreakdown': device_breakdown,
                'topPages': top_pages,
                'trafficSources': traffic_sources
            }
        })
        
    except Exception as e:
        logger.error(f"Error fetching Google Analytics data: {str(e)}")
        return Response({
            'error': str(e),
            'configured': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

