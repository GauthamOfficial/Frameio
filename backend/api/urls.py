from django.urls import path
from . import views

urlpatterns = [
    path('textile/poster/', views.textile_poster, name='textile-poster'),
    # Test endpoint for AI generation without auth
    path('test/two-step/', views.two_step_generation_test, name='two-step-generation-test'),
    # File upload endpoints
    path('upload/', views.upload_file, name='upload-file'),
    path('upload/multiple/', views.upload_multiple_files, name='upload-multiple-files'),
    # AI generation endpoints
    path('ai/post-generation/generate_social_media_post/', views.generate_social_media_post, name='generate-social-media-post'),
    # Contact form endpoint
    path('contact/', views.contact_form, name='contact-form'),
]
