# models.py
import enum
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class OrderStatus(str, enum.Enum):
    pending = "pending"
    partial = "partial"
    executed = "executed"
    cancelled = "cancelled"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    orders = relationship("Order", back_populates="investor")
    tokens = relationship("Token", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = Column(String, primary_key=True, index=True)
    investor_id = Column(Integer, ForeignKey("users.id"))
    security = Column(String, index=True)
    original_qty = Column(Integer)
    executed_qty = Column(Integer, default=0)
    status = Column(Enum(OrderStatus), default=OrderStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    investor = relationship("User", back_populates="orders")

class Token(Base):
    __tablename__ = "tokens"
    token = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="tokens")
