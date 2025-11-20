"""
Aviation App Configuration
"""

from django.apps import AppConfig


class AviationConfig(AppConfig):
    """Aviation app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "aviation"
    verbose_name = "Australian Aviation Data"

    def ready(self):
        """App initialization."""
        # Import signals if needed in future
        pass
