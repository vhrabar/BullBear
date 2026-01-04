from django.apps import AppConfig


class FundsConfig(AppConfig):
    name = 'api.funds'

    def ready(self):
        from . import signals
