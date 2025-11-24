from django.apps import AppConfig


class FlightOperationsConfig(AppConfig):
    """
    Flight Operations App Configuration

    Core CASA flight operations management app providing:
    - Complete flight operations lifecycle management
    - CASA compliance automation for all flight activities
    - Real-time operational monitoring and coordination
    - Integration with all existing apps (rpas, sms, aviation, core)
    - Three-color compliance system integration

    This app serves as the operational heart of the world-class
    aviation management system.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "flight_operations"
    verbose_name = "Flight Operations Management"

    def ready(self):
        """App initialization - import signals and setup"""
        try:
            import flight_operations.signals  # noqa F401
        except ImportError:
            pass
