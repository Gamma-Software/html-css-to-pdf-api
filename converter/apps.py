from django.apps import AppConfig
from health_check.plugins import plugin_dir


class ConverterConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "converter"

    def ready(self):
        from .health_checks import PDFConversionHealthCheck
        plugin_dir.register(PDFConversionHealthCheck)
