from django.apps import AppConfig


class PosterGenerationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'poster_generation'
    verbose_name = 'Poster Generation'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        try:
            import poster_generation.signals  # noqa
        except ImportError:
            pass