import pydantic_settings


class SettingsBase(pydantic_settings.BaseSettings):
    """
    Base settings type for all AskBro configuration objects.

    Acts as a marker for dependency injection wiring while inheriting common Pydantic behaviour.
    """

    class Config:
        extra = "allow"
