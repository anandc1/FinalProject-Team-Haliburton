from sqlalchemy import Column, Integer, String, Boolean
from ..dependencies.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
