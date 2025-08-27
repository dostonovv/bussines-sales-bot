from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime

# 🗂 Category (Kategoriya)
class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    products = relationship("Product", back_populates="category")  # ✅

# 📱 Product (Mahsulot)
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float)
    image_path = Column(String)
    category_id = Column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="products")  # ✅
    orders = relationship("Order", back_populates="product")        # ✅ YETISHGAN QISM

# 📦 Order (Buyurtma)
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, default=1)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    phone_number = Column(String, nullable=True)

    product = relationship("Product", back_populates="orders")      # ✅

# 📊 ActivityLog (Foydalanuvchi faolligi)
class ActivityLog(Base):
    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    hour = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
