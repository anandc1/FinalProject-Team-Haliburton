from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, DATETIME, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    description = Column(String(200), nullable=True)
    discount_percent = Column(Integer, nullable=False)  # 10 = 10% off
    min_order_amount_cents = Column(Integer, nullable=False, default=0)
    max_discount_cents = Column(Integer, nullable=True)  # Maximum discount amount
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DATETIME, nullable=True)
    created_at = Column(DATETIME, nullable=False, server_default=str(datetime.now()))
    usage_limit = Column(Integer, nullable=True)  # NULL = unlimited
    times_used = Column(Integer, default=0, nullable=False)
