from sqlalchemy import Column, ForeignKey, Integer, String, DECIMAL, DATETIME
from sqlalchemy.orm import relationship
from datetime import datetime
from ..dependencies.database import Base

class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    dish_id = Column(Integer, ForeignKey("dishes.id"))
    qty = Column(Integer, index=True, nullable=False)
    unit_price_cents = Column(Integer, nullable=False)
    line_total_cents = Column(Integer, nullable=False)

    dish = relationship("Dish")
    order = relationship("Order", back_populates="order_details")
