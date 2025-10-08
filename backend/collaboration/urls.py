from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DesignShareViewSet,
    DesignCommentViewSet,
    DesignCollaborationViewSet,
    DesignVersionViewSet,
    DesignActivityViewSet,
    CollaborationAPIView
)

router = DefaultRouter()
router.register(r'shares', DesignShareViewSet, basename='design-shares')
router.register(r'comments', DesignCommentViewSet, basename='design-comments')
router.register(r'collaborations', DesignCollaborationViewSet, basename='design-collaborations')
router.register(r'versions', DesignVersionViewSet, basename='design-versions')
router.register(r'activities', DesignActivityViewSet, basename='design-activities')
router.register(r'api', CollaborationAPIView, basename='collaboration-api')

urlpatterns = [
    path('', include(router.urls)),
]
