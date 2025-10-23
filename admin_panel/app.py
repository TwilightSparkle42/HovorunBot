from fastadmin import fastapi_app as admin_app  # type: ignore[import-untyped]
from fastapi import FastAPI

from .admin_models import *  # noqa: F401, F403

# Main application for our project
app = FastAPI()


# Mount FastAdmin's FastAPI application under /admin
app.mount("/admin", admin_app)
