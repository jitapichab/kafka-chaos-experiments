from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class OrderState(str, Enum):
    pending = 'pending'
    rejected = 'rejected'
    failed = 'failed'
    success = 'success'
    reversed = 'reversed'


class PokeOrderCreate(BaseModel):
    user_id: int
    pokemon: str
    country: str
    price: float


class PokeOrderUpdate(BaseModel):
    state: OrderState


class PokeOrder(BaseModel):
    id: int
    user_id: int
    pokemon: str
    country: str
    price: float
    state: OrderState
    timestamp: datetime

    class Config:
        orm_mode = True
