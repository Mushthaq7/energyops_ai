from typing import Any
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    id: Any
    # Generate __tablename__ automatically
    # @declared_attr
    # def __tablename__(cls) -> str:
    #     return cls.__name__.lower()
