from django.apps import AppConfig


class CollaborationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'collaboration'
    verbose_name = 'Collaboration'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        try:
            import collaboration.signals  # noqa
        except ImportError:
            pass