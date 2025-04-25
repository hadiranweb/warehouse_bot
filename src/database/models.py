from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

class Role(enum.Enum):
    SELLER = "seller"
    CUSTOMER = "customer"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    role = Column(Enum(Role))
    name = Column(String)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    email = Column(String, nullable=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String, unique=True)
    description = Column(String, nullable=True)
    category = Column(String, nullable=True)
    price = Column(Float, nullable=True)

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    type = Column(String)  # خرید/پرداخت
    amount = Column(Float, nullable=True)
    date = Column(DateTime)
    user = relationship("User")
    product = relationship("Product")

class Reminder(Base):
    __tablename__ = "reminders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String)
    date = Column(DateTime)
    repeat = Column(String, nullable=True)  # روزانه/هفتگی
    user = relationship("User")
