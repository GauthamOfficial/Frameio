from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, UserProfileViewSet, UserActivityViewSet, CompanyProfileViewSet
from .auth_views import CustomTokenObtainPairView, register, logout, me
from .verification_views import send_verification_email_view, verify_email, check_verification_status
from . import google_analytics_views

# TEST ENDPOINT - completely bypasses DRF
def test_endpoint(request):
    return JsonResponse({'status': 'success', 'message': 'Django is working!', 'debug_mode': True})

# Create router for user-related views
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'activities', UserActivityViewSet, basename='activity')
router.register(r'company-profiles', CompanyProfileViewSet, basename='company-profile')

urlpatterns = [
    path('test/', test_endpoint, name='test'),
    path('', include(router.urls)),
    # Authentication endpoints (under /api/users/auth/)
    path('users/auth/register/', register, name='register'),
    path('users/auth/login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('users/auth/logout/', logout, name='logout'),
    path('users/auth/me/', me, name='me'),
    path('users/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Email verification endpoints
    path('users/auth/send-verification-email/', send_verification_email_view, name='send_verification_email'),
    path('users/auth/verify-email/<str:token>/', verify_email, name='verify_email'),
    path('users/auth/verification-status/', check_verification_status, name='verification_status'),
    # Google Analytics endpoints
    path('admin/analytics/', google_analytics_views.google_analytics_all, name='google-analytics-all'),
    path('admin/analytics/overview/', google_analytics_views.google_analytics_overview, name='google-analytics-overview'),
    path('admin/analytics/user-growth/', google_analytics_views.google_analytics_user_growth, name='google-analytics-user-growth'),
    path('admin/analytics/device-breakdown/', google_analytics_views.google_analytics_device_breakdown, name='google-analytics-device-breakdown'),
    path('admin/analytics/top-pages/', google_analytics_views.google_analytics_top_pages, name='google-analytics-top-pages'),
    path('admin/analytics/traffic-sources/', google_analytics_views.google_analytics_traffic_sources, name='google-analytics-traffic-sources'),
]
