from sqlalchemy.orm import DeclarativeBase


class BaseModel(DeclarativeBase):
    """
    Declarative SQLAlchemy base for all ORM models.

    Models extending this base get shared metadata for migrations and schema inspection.
    """

    pass
