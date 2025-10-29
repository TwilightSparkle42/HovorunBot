"""FastAPI application entry point for the admin panel."""

from fastadmin import fastapi_app as admin_app  # type: ignore[import-untyped]
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from .admin_models.user import UserAdmin  # noqa: F401

app = FastAPI()
app.mount("/admin", admin_app)


@app.get("/")
def home_page() -> RedirectResponse:
    return RedirectResponse("/admin")
