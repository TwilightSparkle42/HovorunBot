from injector import Binder, Module


class AdminPanelModule(Module):
    """
    Configure dependency injection bindings for AI providers.

    Instantiates concrete AI clients and registers them within the shared registry.
    """

    def configure(self, binder: Binder) -> None:
        pass
