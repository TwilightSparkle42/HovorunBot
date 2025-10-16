import pydantic_settings


class SettingsBase(pydantic_settings.BaseSettings):
    """
    Basic settings class for all settings of AskBro application.

    Used as a label class for some checks as well as for DI injection.
    """

    class Config:
        extra = "allow"
