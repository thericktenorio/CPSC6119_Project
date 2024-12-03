from django.apps import AppConfig


class ApplicationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "application"

    def ready(self):
        from .patterns.observer import TINObserver, AdvisoryObserver

        self.tin_observer = TINObserver()
        self.advisory_observer = AdvisoryObserver()

    # Session Mangement: one session per user
    #def ready(self):
    #    import application.signals  # Imports logout_previous_sessions() from signals.py when app is started