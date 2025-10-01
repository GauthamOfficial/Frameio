from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Create router for AI service-related views
router = DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
]
