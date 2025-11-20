from django.apps import AppConfig


class DesignExportConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'design_export'
    verbose_name = 'Design Export'
    
    def ready(self):
        """Import signal handlers when the app is ready"""
        try:
            import design_export.signals  # noqa
        except ImportError:
            pass