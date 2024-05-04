from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class Courier(BaseModel):
    __tablename__ = "courier"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True)
    districts = Column(String)
    avg_order_complete_time = Column(DateTime, default=func.now())
    avg_day_orders = Column(Integer, default=0)
    active_order = relationship("Order", back_populates="id_courier", cascade="all, delete-orphan")


class Order(BaseModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    district = Column(String)
    status = Column(Integer, default=1)  # 1 - в работе, 2 - завершен

    courier_id = Column(Integer, ForeignKey("courier.id"))
    id_courier = relationship("Courier", back_populates="active_order", lazy="selectin")
