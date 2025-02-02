# schemas.py
from pydantic import BaseModel
from typing import List

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserCreate(BaseModel):
    username: str
    password: str

class OrderCreate(BaseModel):
    security: str
    qty: int

class OrderAmend(BaseModel):
    qty: int

class OrderExecute(BaseModel):
    executed_qty: int

class OrderResponse(BaseModel):
    id: str
    security: str
    original_qty: int
    executed_qty: int
    status: str
    pending_qty: int

    class Config:
        orm_mode = True

class PortfolioItem(BaseModel):
    security: str
    qty: int
