from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = ('django.db.models.BigAutoField')
    name = 'api.trading'

    def ready(self):
        from . import signals
