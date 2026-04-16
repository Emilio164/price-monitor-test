from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base, Product, PriceHistory
from datetime import datetime
import os

# Default path relative to project root
DEFAULT_DB_PATH = os.path.join("data", "price_monitor.db")
# Prioritize environment variable (for Cloud) over local SQLite
DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# Fix for Heroku/Cloud providers that use 'postgres://' instead of 'postgresql://'
if DB_URL and DB_URL.startswith("postgres://"):
    DB_URL = DB_URL.replace("postgres://", "postgresql://", 1)

class DatabaseManager:
    def __init__(self, db_url=DB_URL):
        # Solo crear directorios si usamos SQLite local
        if "sqlite" in db_url:
            db_path = db_url.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()

    def add_product(self, name, url, store, group_name=None, category=None):
        session = self.get_session()
        try:
            # Check if product already exists
            existing = session.query(Product).filter(Product.url == url).first()
            if existing:
                return existing
            
            new_product = Product(
                name=name,
                group_name=group_name,
                url=url,
                store=store,
                category=category
            )
            session.add(new_product)
            session.commit()
            session.refresh(new_product)
            return new_product
        finally:
            session.close()

    def get_all_products(self):
        session = self.get_session()
        try:
            return session.query(Product).all()
        finally:
            session.close()

    def add_price_entry(self, product_id, price, is_out_of_stock):
        session = self.get_session()
        try:
            # Check last entry to avoid duplicates (same price on same day)
            last_entry = session.query(PriceHistory).filter(
                PriceHistory.product_id == product_id
            ).order_by(PriceHistory.timestamp.desc()).first()
            
            now = datetime.utcnow()
            
            if last_entry:
                same_day = last_entry.timestamp.date() == now.date()
                same_price = abs(last_entry.price - price) < 0.01 # Float comparison
                
                if same_day and same_price:
                    # Don't add if it's the same price on the same day
                    return last_entry

            new_entry = PriceHistory(
                product_id=product_id,
                price=price,
                is_out_of_stock=1 if is_out_of_stock else 0,
                timestamp=now
            )
            session.add(new_entry)
            
            # Update product's last and min price
            product = session.query(Product).get(product_id)
            if product:
                product.last_price = price
                if product.min_price is None or (price > 0 and price < product.min_price):
                    product.min_price = price
            
            session.commit()
            return new_entry
        finally:
            session.close()

    def get_product_history(self, product_id):
        session = self.get_session()
        try:
            return session.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(PriceHistory.timestamp.asc()).all()
        finally:
            session.close()

    def get_trend_data(self, product_id):
        """Returns (current_price, previous_price)"""
        session = self.get_session()
        try:
            entries = session.query(PriceHistory).filter(
                PriceHistory.product_id == product_id
            ).order_by(PriceHistory.timestamp.desc()).limit(2).all()
            
            if len(entries) < 2:
                # Return current and 0 if not enough history
                return (entries[0].price if entries else 0, 0)
            return (entries[0].price, entries[1].price)
        finally:
            session.close()

    def get_median_price(self, product_id, days=30):
        """Calculates the median price for the last N days"""
        import statistics
        from datetime import datetime, timedelta
        session = self.get_session()
        try:
            since_date = datetime.utcnow() - timedelta(days=days)
            entries = session.query(PriceHistory.price).filter(
                PriceHistory.product_id == product_id,
                PriceHistory.timestamp >= since_date,
                PriceHistory.price > 0
            ).all()
            
            prices = [e[0] for e in entries]
            if not prices:
                return 0
            return statistics.median(prices)
        finally:
            session.close()

    def delete_product(self, product_id):
        session = self.get_session()
        try:
            product = session.query(Product).get(product_id)
            if product:
                session.delete(product)
                session.commit()
                return True
            return False
        finally:
            session.close()
