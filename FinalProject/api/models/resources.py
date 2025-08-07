from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300), nullable=True)
    amount = Column(Integer, nullable=False, default=0)
    unit = Column(String(50), nullable=False, default="units")  # kg, lbs, pieces, etc.
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    updated_at = Column(DATETIME, nullable=False, server_default=str(datetime.now()), onupdate=datetime.now)

    recipes = relationship("Recipe", back_populates="resource")
