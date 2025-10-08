from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, textile_views, scheduling_views, test_views, file_upload_views, social_media_views, catalog_views, fabric_views

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
router.register(r'background', views.BackgroundMatcherViewSet, basename='background-matcher')

# Phase 1 Week 3 - Textile-specific endpoints
router.register(r'textile/poster', textile_views.TextilePosterViewSet, basename='textile-poster-new')
router.register(r'textile/caption', textile_views.TextileCaptionViewSet, basename='textile-caption')

# Phase 1 Week 3 - Scheduling system endpoints
router.register(r'schedule', scheduling_views.ScheduledPostViewSet, basename='scheduled-post')

# Social Media Posting endpoints
router.register(r'social', social_media_views.SocialMediaPostViewSet, basename='social-media')

# Catalog Builder endpoints
router.register(r'catalog', catalog_views.CatalogBuilderViewSet, basename='catalog-builder')

# Phase 1 Week 4 - Advanced AI Services
router.register(r'fabric', fabric_views.FabricAnalysisViewSet, basename='fabric-analysis')

urlpatterns = [
    path('', include(router.urls)),
    
    # File Upload URLs
    path('upload/', file_upload_views.upload_file, name='upload-file'),
    path('upload/multiple/', file_upload_views.upload_multiple_files, name='upload-multiple-files'),
    path('upload/info/<str:filename>/', file_upload_views.get_file_info, name='get-file-info'),
    path('upload/<str:filename>/', file_upload_views.delete_file, name='delete-file'),
    
    # Test interface URLs
    path('test/', test_views.test_interface, name='test-interface'),
    path('test/poster/', test_views.test_poster_generation, name='test-poster'),
    path('test/caption/', test_views.test_caption_generation, name='test-caption'),
    path('test/schedule/', test_views.test_schedule_creation, name='test-schedule'),
    path('test/analytics/', test_views.test_analytics, name='test-analytics'),
]
