from sqlalchemy import Column, Integer, String, Enum, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()


class OrderState(str, enum.Enum):
    pending = 'pending'
    rejected = 'rejected'
    failed = 'failed'
    success = 'success'
    reversed = 'reversed'


class PokeOrder(Base):
    __tablename__ = "poke_orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    pokemon = Column(String, index=True)
    country = Column(String, index=True)
    price = Column(Float, nullable=False)
    state = Column(Enum(OrderState),
                   default=OrderState.pending,
                   nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
