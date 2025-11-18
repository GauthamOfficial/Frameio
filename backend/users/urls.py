from django.urls import path, include
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from .views import UserViewSet, UserProfileViewSet, UserActivityViewSet, CompanyProfileViewSet

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
]
