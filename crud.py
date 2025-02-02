# crud.py
import uuid
from sqlalchemy.orm import Session
from models import User, Order, Token, OrderStatus
import schemas
from auth import get_password_hash, verify_password

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_token(db: Session, user: User):
    token_str = str(uuid.uuid4())
    token = Token(token=token_str, user_id=user.id)
    db.add(token)
    db.commit()
    return token_str

def get_user_by_token(db: Session, token_str: str):
    token = db.query(Token).filter(Token.token == token_str).first()
    if token:
        return token.user
    return None

def create_order(db: Session, investor_id: int, order: schemas.OrderCreate):
    order_id = str(uuid.uuid4())
    new_order = Order(
        id=order_id,
        investor_id=investor_id,
        security=order.security,
        original_qty=order.qty,
        executed_qty=0,
        status=OrderStatus.pending
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

def get_order(db: Session, order_id: str):
    return db.query(Order).filter(Order.id == order_id).first()

def amend_order(db: Session, order: Order, new_qty: int):
    if new_qty < order.executed_qty:
        raise ValueError("New quantity cannot be less than executed quantity")
    order.original_qty = new_qty
    # Update status based on the execution so far
    if order.executed_qty == new_qty:
        order.status = OrderStatus.executed
    elif order.executed_qty > 0:
        order.status = OrderStatus.partial
    else:
        order.status = OrderStatus.pending
    db.commit()
    db.refresh(order)
    return order

def cancel_order(db: Session, order: Order):
    order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(order)
    return order

def execute_order(db: Session, order: Order, executed_qty: int):
    if executed_qty <= 0:
        raise ValueError("Executed quantity must be positive")
    if order.executed_qty + executed_qty > order.original_qty:
        raise ValueError("Execution quantity exceeds pending order quantity")
    order.executed_qty += executed_qty
    if order.executed_qty == order.original_qty:
        order.status = OrderStatus.executed
    else:
        order.status = OrderStatus.partial
    db.commit()
    db.refresh(order)
    return order

def list_orders(db: Session, investor_id: int):
    return db.query(Order).filter(Order.investor_id == investor_id).all()

def get_portfolio(db: Session, investor_id: int):
    orders = db.query(Order).filter(Order.investor_id == investor_id).all()
    portfolio = {}
    for order in orders:
        if order.executed_qty > 0:
            portfolio[order.security] = portfolio.get(order.security, 0) + order.executed_qty
    return portfolio
