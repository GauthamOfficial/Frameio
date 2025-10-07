from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, textile_views, scheduling_views, test_views

# Create router for AI service-related views
router = DefaultRouter()
router.register(r'providers', views.AIProviderViewSet, basename='ai-provider')
router.register(r'generation-requests', views.AIGenerationRequestViewSet, basename='ai-generation-request')
router.register(r'quotas', views.AIUsageQuotaViewSet, basename='ai-quota')
router.register(r'templates', views.AITemplateViewSet, basename='ai-template')
router.register(r'analytics', views.AIAnalyticsViewSet, basename='ai-analytics')

# New AI Services for Phase 1 Week 1 Member 3 tasks
router.register(r'poster', views.TextilePosterViewSet, basename='textile-poster')
router.register(r'festival-kit', views.FestivalKitViewSet, basename='festival-kit')
router.register(r'catalog', views.CatalogBuilderViewSet, basename='catalog-builder')
router.register(r'background', views.BackgroundMatcherViewSet, basename='background-matcher')

# Phase 1 Week 3 - Textile-specific endpoints
router.register(r'textile/poster', textile_views.TextilePosterViewSet, basename='textile-poster-new')
router.register(r'textile/caption', textile_views.TextileCaptionViewSet, basename='textile-caption')

# Phase 1 Week 3 - Scheduling system endpoints
router.register(r'schedule', scheduling_views.ScheduledPostViewSet, basename='scheduled-post')

urlpatterns = [
    path('', include(router.urls)),
    # Test interface URLs
    path('test/', test_views.test_interface, name='test-interface'),
    path('test/poster/', test_views.test_poster_generation, name='test-poster'),
    path('test/caption/', test_views.test_caption_generation, name='test-caption'),
    path('test/schedule/', test_views.test_schedule_creation, name='test-schedule'),
    path('test/analytics/', test_views.test_analytics, name='test-analytics'),
]
