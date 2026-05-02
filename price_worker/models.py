from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Numeric, DateTime, JSON, CHAR
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Store(Base):
    __tablename__ = "stores"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    website_url = Column(String(500))
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("categories.id"))
    slug = Column(String(255), unique=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(500), nullable=False)
    brand = Column(String(255))
    category_id = Column(Integer, ForeignKey("categories.id"))
    attributes = Column(JSON)
    ean = Column(String(13))
    image_url = Column(String(1000))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Price(Base):
    __tablename__ = "prices"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    old_price = Column(Numeric(10, 2))
    currency = Column(CHAR(3), default="AMD")
    url = Column(String(1000), nullable=False)
    scraped_at = Column(DateTime(timezone=True), nullable=False)
    valid_from = Column(DateTime(timezone=True), server_default=func.now())
    valid_to = Column(DateTime(timezone=True))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True)
    password_hash = Column(String(255))
    notification_prefs = Column(JSON)
    shopping_lists = relationship("ShoppingList", back_populates="user")

class ShoppingList(Base):
    __tablename__ = "shopping_lists"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    items = Column(JSON)
    user = relationship("User", back_populates="shopping_lists")
