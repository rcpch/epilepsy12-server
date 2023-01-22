from django.apps import AppConfig


class Epilepsy12Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'epilepsy12'

    def ready(self) -> None:
        import epilepsy12.signals
        return super().ready()
