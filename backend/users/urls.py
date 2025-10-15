from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, UserProfileViewSet, UserActivityViewSet, CompanyProfileViewSet

# Create router for user-related views
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'activities', UserActivityViewSet, basename='activity')
router.register(r'company-profiles', CompanyProfileViewSet, basename='company-profile')

urlpatterns = [
    path('', include(router.urls)),
]
