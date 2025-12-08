"""
URL configuration for frameio_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
# Removed image generation test imports

def api_status(request):
    """Simple API status endpoint for the root URL"""
    return JsonResponse({
        'status': 'success',
        'message': 'Framio API is running',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'api_docs': '/api/schema/',
            'swagger': '/api/docs/',
            'redoc': '/api/redoc/',
            'organizations': '/api/organizations/',
            'users': '/api/users/',
            'designs': '/api/designs/',
            'ai_services': '/api/ai/',
            'fabric_analysis': '/api/ai/fabric/',
            'text_generation': '/api/ai/text-generation/',
            'content_analysis': '/api/ai/content-analysis/',
            'design_export': '/api/design-export/',
            'collaboration': '/api/collaboration/'
        }
    })

def health_check(request):
    """Health check endpoint for testing connectivity"""
    return JsonResponse({
        'status': 'healthy',
        'message': 'Backend server is running',
        'timestamp': timezone.now().isoformat()
    })

def test_interface(request):
    return api_status(request)

def ai_image_generation_test(request):
    return api_status(request)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api_status, name="api_status"),
    path("health/", health_check, name="health_check"),
    path("health", health_check, name="health_check_no_slash"),
    # Deprecated test routes kept as no-ops returning status for compatibility
    path("test/", test_interface, name="test_interface"),
    path("ai-image-generation-test/", ai_image_generation_test, name="ai_image_generation_test"),
    path("ai_image_generation_test.html", RedirectView.as_view(url="/", permanent=True)),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # API Endpoints
    path("api/", include("organizations.urls")),
    path("api/", include("users.urls")),
    path("api/", include("designs.urls")),
    path("api/ai/", include("ai_services.urls")),
    path("api/", include("api.urls")),  # API endpoints
    # Removed poster generation URLs
    path("api/design-export/", include("design_export.urls")),
    path("api/collaboration/", include("collaboration.urls")),
    
    # Test endpoints (no authentication required)
    # Removed image generation test endpoints
]

# Serve media files in development
# In production, Nginx should serve media files directly (see nginx.conf)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
