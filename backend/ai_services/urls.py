from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, scheduling_views, file_upload_views, social_media_views, catalog_views, fabric_views, post_generation_views, ai_poster_views, ai_caption_views

# Create router for AI service-related views
router = DefaultRouter()
router.register(r'providers', views.AIProviderViewSet, basename='ai-provider')
router.register(r'generation-requests', views.AIGenerationRequestViewSet, basename='ai-generation-request')
router.register(r'quotas', views.AIUsageQuotaViewSet, basename='ai-quota')
router.register(r'templates', views.AITemplateViewSet, basename='ai-template')
router.register(r'analytics', views.AIAnalyticsViewSet, basename='ai-analytics')

# Text generation and content analysis endpoints
router.register(r'text-generation', views.TextGenerationViewSet, basename='text-generation')
router.register(r'content-analysis', views.ContentAnalysisViewSet, basename='content-analysis')

# Phase 1 Week 3 - Scheduling system endpoints
router.register(r'schedule', scheduling_views.ScheduledPostViewSet, basename='scheduled-post')

# Social Media Posting endpoints
router.register(r'social', social_media_views.SocialMediaPostViewSet, basename='social-media')

# Catalog Builder endpoints
router.register(r'catalog', catalog_views.CatalogBuilderViewSet, basename='catalog-builder')

# Phase 1 Week 4 - Advanced AI Services
router.register(r'fabric', fabric_views.FabricAnalysisViewSet, basename='fabric-analysis')

# AI Post Generation endpoints
router.register(r'post-generation', post_generation_views.AIPostGenerationViewSet, basename='ai-post-generation')

urlpatterns = [
    path('', include(router.urls)),
    
    # File Upload URLs
    path('upload/', file_upload_views.upload_file, name='upload-file'),
    path('upload/multiple/', file_upload_views.upload_multiple_files, name='upload-multiple-files'),
    path('upload/info/<str:filename>/', file_upload_views.get_file_info, name='get-file-info'),
    path('upload/<str:filename>/', file_upload_views.delete_file, name='delete-file'),
    
    # AI Poster Generation URLs
    path('ai-poster/generate_poster/', ai_poster_views.generate_poster, name='generate-poster'),
    path('ai-poster/edit_poster/', ai_poster_views.edit_poster, name='edit-poster'),
    path('ai-poster/composite_poster/', ai_poster_views.composite_poster, name='composite-poster'),
    path('ai-poster/status/', ai_poster_views.poster_service_status, name='poster-service-status'),
    
    # AI Caption Generation URLs
    path('ai-caption/product_caption/', ai_caption_views.generate_product_caption, name='generate-product-caption'),
    path('ai-caption/social_media_caption/', ai_caption_views.generate_social_media_caption, name='generate-social-media-caption'),
    path('ai-caption/image_caption/', ai_caption_views.generate_image_caption, name='generate-image-caption'),
    path('ai-caption/bulk_captions/', ai_caption_views.generate_bulk_captions, name='generate-bulk-captions'),
    path('ai-caption/status/', ai_caption_views.caption_service_status, name='caption-service-status'),
]
