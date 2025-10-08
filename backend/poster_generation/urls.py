from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PosterGenerationJobViewSet,
    PosterTemplateViewSet,
    PosterGenerationHistoryViewSet,
    PosterGenerationAPIView
)

router = DefaultRouter()
router.register(r'jobs', PosterGenerationJobViewSet, basename='poster-jobs')
router.register(r'templates', PosterTemplateViewSet, basename='poster-templates')
router.register(r'history', PosterGenerationHistoryViewSet, basename='poster-history')
router.register(r'api', PosterGenerationAPIView, basename='poster-api')

urlpatterns = [
    path('', include(router.urls)),
]
