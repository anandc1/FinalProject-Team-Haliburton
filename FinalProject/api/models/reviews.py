from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_number = Column(String(50), ForeignKey("orders.order_number"), nullable=False)
    customer_name = Column(String(100), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)
    is_approved = Column(Boolean, default=False, nullable=False)
    created_at = Column(DATETIME, nullable=False, server_default=str(datetime.now()))

    order = relationship("Order")
