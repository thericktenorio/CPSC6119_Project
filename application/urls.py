from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name = "home"),
    path("logout/", views.logout_user, name = "logout"),
    path("register/", views.register_user, name = "register"),
    path("auto_update_client/", views.auto_update_client, name = "auto_update_client"),
    path("create_new_client/", views.create_new_client, name = "create_new_client"),
    path("delete_client/", views.delete_client, name = "delete_client"),
    path("import_clients/", views.import_clients, name = "import_clients"),
    path("export_clients/", views.export_clients, name = "export_clients"),
    path("list_users/", views.list_users, name = "list_users"),
    path("audit_client_logs/", views.audit_client_logs, name = "audit_client_logs")
]