from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, scheduling_views, file_upload_views, social_media_views, fabric_views, post_generation_views, ai_poster_views, ai_caption_views, branding_kit_views

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
    path('ai-poster/add_text_overlay/', ai_poster_views.add_text_overlay, name='add-text-overlay'),
    path('ai-poster/status/', ai_poster_views.poster_service_status, name='poster-service-status'),
    path('ai-poster/poster/<str:poster_id>/', ai_poster_views.get_poster, name='get-poster'),
    
    # AI Caption Generation URLs
    path('ai-caption/product_caption/', ai_caption_views.generate_product_caption, name='generate-product-caption'),
    path('ai-caption/social_media_caption/', ai_caption_views.generate_social_media_caption, name='generate-social-media-caption'),
    path('ai-caption/image_caption/', ai_caption_views.generate_image_caption, name='generate-image-caption'),
    path('ai-caption/bulk_captions/', ai_caption_views.generate_bulk_captions, name='generate-bulk-captions'),
    path('ai-caption/status/', ai_caption_views.caption_service_status, name='caption-service-status'),
    
    # Branding Kit Generation URLs
    path('branding-kit/generate/', branding_kit_views.generate_branding_kit, name='generate-branding-kit'),
    path('branding-kit/logo/', branding_kit_views.generate_logo, name='generate-logo'),
    path('branding-kit/colors/', branding_kit_views.generate_color_palette, name='generate-color-palette'),
    path('branding-kit/status/', branding_kit_views.branding_kit_status, name='branding-kit-status'),
    path('branding-kit/test-colors/', branding_kit_views.test_color_detection, name='test-color-detection'),
]
