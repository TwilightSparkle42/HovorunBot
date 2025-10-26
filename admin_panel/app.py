"""FastAPI application entry point for the admin panel."""

from fastapi import FastAPI

from admin_panel.auth_backend import AdminPanelAuthBackend
from admin_panel.views.user import UserAdmin
from di_config import get_injector

from .common import Admin
from .views.chat import ChatAdmin

app = FastAPI()

injector = get_injector()

auth_backend = injector.create_object(AdminPanelAuthBackend)

admin = injector.create_object(
    Admin,
    additional_kwargs={"app": app, "authentication_backend": auth_backend},
)

admin.add_view(UserAdmin)
admin.add_view(ChatAdmin)
