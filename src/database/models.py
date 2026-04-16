from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False) # Nombre específico de la tienda
    group_name = Column(String, nullable=True) # Nombre común para agrupamiento
    url = Column(String, unique=True, nullable=False)
    store = Column(String, nullable=False)
    category = Column(String)
    last_price = Column(Float)
    min_price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    prices = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")

class PriceHistory(Base):
    __tablename__ = 'price_history'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_out_of_stock = Column(Integer, default=0) # 0: False, 1: True
    
    product = relationship("Product", back_populates="prices")
