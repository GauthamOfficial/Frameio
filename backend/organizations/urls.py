from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, OrganizationMemberViewSet, OrganizationInvitationViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'members', OrganizationMemberViewSet, basename='member')
router.register(r'invitations', OrganizationInvitationViewSet, basename='invitation')

urlpatterns = [
    path('', include(router.urls)),
]
