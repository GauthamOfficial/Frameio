from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

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

urlpatterns = [
    path('', include(router.urls)),
]
