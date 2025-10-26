from typing import Sequence
from urllib.parse import urljoin

from injector import Inject
from sqladmin import Admin as _SqlAdmin
from sqladmin import BaseView, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.applications import Starlette
from starlette.middleware import Middleware

from database.connection import DatabaseConnection
from di_config import get_injector
from settings.admin import AdminSettings
from utils.di import PLACEHOLDER


class Admin(_SqlAdmin):
    """Wrapper to replace properties populated on startup with injections from settings and di_context"""

    def __init__(
        self,
        app: Starlette,
        authentication_backend: AuthenticationBackend | None = None,
        middlewares: Sequence[Middleware] | None = None,
        db_connection: Inject[DatabaseConnection] = PLACEHOLDER,
        admin_settings: Inject[AdminSettings] = PLACEHOLDER,
    ) -> None:
        self._injector = get_injector()
        engine = db_connection.engine
        session_maker = db_connection.session_maker
        base_url = admin_settings.base_url
        title = admin_settings.title
        logo_url = admin_settings.logo_url
        favicon_url = admin_settings.favicon_url
        templates_dir = admin_settings.templates_dir
        debug = admin_settings.debug
        super().__init__(
            app,
            authentication_backend=authentication_backend,
            middlewares=middlewares,
            engine=engine,
            session_maker=session_maker,
            base_url=base_url,
            title=title,
            logo_url=logo_url,
            favicon_url=favicon_url,
            templates_dir=templates_dir,
            debug=debug,
        )

    # Wrapped original function to resolve injecting dependencies
    def add_model_view(self, view: type[ModelView]) -> None:
        """Add ModelView to the Admin.

        ???+ usage
            ```python
            from sqladmin import Admin, ModelView

            class UserAdmin(ModelView, model=User):
                pass

            admin.add_model_view(UserAdmin)
            ```
        """

        # Set database engine from Admin instance
        view.session_maker = self.session_maker
        view.is_async = self.is_async
        view.ajax_lookup_url = urljoin(self.base_url + "/", f"{view.identity}/ajax/lookup")
        view.templates = self.templates
        view_instance = self._injector.create_object(view)

        self._find_decorated_funcs(view, view_instance, self._handle_action_decorated_func)

        self._find_decorated_funcs(view, view_instance, self._handle_expose_decorated_func)

        self._views.append(view_instance)
        self._build_menu(view_instance)

    def add_base_view(self, view: type[BaseView]) -> None:
        """Add BaseView to the Admin.

        ???+ usage
            ```python
            from sqladmin import BaseView, expose

            class CustomAdmin(BaseView):
                name = "Custom Page"
                icon = "fa-solid fa-chart-line"

                @expose("/custom", methods=["GET"])
                async def test_page(self, request: Request):
                    return await self.templates.TemplateResponse(request, "custom.html")

            admin.add_base_view(CustomAdmin)
            ```
        """

        view.templates = self.templates
        view_instance = self._injector.create_object(view)

        self._find_decorated_funcs(view, view_instance, self._handle_expose_decorated_func)
        self._views.append(view_instance)
        self._build_menu(view_instance)
