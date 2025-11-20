from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExportJobViewSet,
    ExportTemplateViewSet,
    ExportHistoryViewSet,
    ExportAPIView
)

router = DefaultRouter()
router.register(r'jobs', ExportJobViewSet, basename='export-jobs')
router.register(r'templates', ExportTemplateViewSet, basename='export-templates')
router.register(r'history', ExportHistoryViewSet, basename='export-history')
router.register(r'api', ExportAPIView, basename='export-api')

urlpatterns = [
    path('', include(router.urls)),
]
