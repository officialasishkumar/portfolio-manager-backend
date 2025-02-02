# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List

import models
import schemas
import crud
from database import engine
from auth import get_current_user, get_db
from fastapi.middleware.cors import CORSMiddleware

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mock Exchange")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/login", response_model=schemas.TokenSchema)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    token_str = crud.create_token(db, user)
    return {"access_token": token_str, "token_type": "bearer"}

# Optional: Create a user (for testing/demo purposes)
@app.post("/users", response_model=schemas.UserCreate)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    created_user = crud.create_user(db, user)
    # In a real app you wouldn’t return the password
    return {"username": created_user.username, "password": "Hidden"}

@app.post("/orders", response_model=schemas.OrderResponse)
def place_order(order: schemas.OrderCreate, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    new_order = crud.create_order(db, current_user.id, order)
    return schemas.OrderResponse(
        id=new_order.id,
        security=new_order.security,
        original_qty=new_order.original_qty,
        executed_qty=new_order.executed_qty,
        status=new_order.status.value,
        pending_qty=new_order.original_qty - new_order.executed_qty
    )

@app.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def amend_order(order_id: str, amendment: schemas.OrderAmend, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.investor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status in [models.OrderStatus.executed, models.OrderStatus.cancelled]:
        raise HTTPException(status_code=400, detail="Cannot amend fully executed or cancelled order")
    try:
        order = crud.amend_order(db, order, amendment.qty)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.OrderResponse(
        id=order.id,
        security=order.security,
        original_qty=order.original_qty,
        executed_qty=order.executed_qty,
        status=order.status.value,
        pending_qty=order.original_qty - order.executed_qty
    )

@app.delete("/orders/{order_id}", response_model=schemas.OrderResponse)
def cancel_order(order_id: str, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.investor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status in [models.OrderStatus.executed, models.OrderStatus.cancelled]:
        raise HTTPException(status_code=400, detail="Cannot cancel executed or already cancelled order")
    order = crud.cancel_order(db, order)
    return schemas.OrderResponse(
        id=order.id,
        security=order.security,
        original_qty=order.original_qty,
        executed_qty=order.executed_qty,
        status=order.status.value,
        pending_qty=order.original_qty - order.executed_qty
    )

@app.get("/orders", response_model=List[schemas.OrderResponse])
def list_orders(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    orders = crud.list_orders(db, current_user.id)
    return [
        schemas.OrderResponse(
            id=o.id,
            security=o.security,
            original_qty=o.original_qty,
            executed_qty=o.executed_qty,
            status=o.status.value,
            pending_qty=o.original_qty - o.executed_qty
        )
        for o in orders
    ]

@app.get("/portfolio", response_model=List[schemas.PortfolioItem])
def portfolio(current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    portfolio_data = crud.get_portfolio(db, current_user.id)
    return [schemas.PortfolioItem(security=sec, qty=qty) for sec, qty in portfolio_data.items()]

@app.post("/orders/{order_id}/execute", response_model=schemas.OrderResponse)
def execute_order(order_id: str, execution: schemas.OrderExecute, current_user = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud.get_order(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.investor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your order")
    if order.status in [models.OrderStatus.executed, models.OrderStatus.cancelled]:
        raise HTTPException(status_code=400, detail="Order already executed or cancelled")
    try:
        order = crud.execute_order(db, order, execution.executed_qty)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return schemas.OrderResponse(
        id=order.id,
        security=order.security,
        original_qty=order.original_qty,
        executed_qty=order.executed_qty,
        status=order.status.value,
        pending_qty=order.original_qty - order.executed_qty
    )
