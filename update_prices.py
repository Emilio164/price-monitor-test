import asyncio
import random
import sys
import os

# Asegurar que la raíz del proyecto esté en el path para las importaciones de 'src'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db_manager import DatabaseManager
from src.scrapers.fullh4rd_scraper import FullH4rdScraper
from src.scrapers.compragamer_scraper import CompragamerScraper

async def update_all_prices():
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    products = db_manager.get_all_products()
    if not products:
        print("No hay productos para actualizar.")
        return

    print(f"Iniciando actualización de {len(products)} productos...")
    
    for i, product in enumerate(products):
        # Delay aleatorio para evitar baneos
        if i > 0:
            delay = random.uniform(5.0, 10.0)
            print(f"Esperando {delay:.1f}s...")
            await asyncio.sleep(delay)
        
        print(f"Procesando: {product.name} ({product.store})...")
        
        scraper = None
        if product.store == "FullH4rd":
            scraper = FullH4rdScraper(product.url)
        elif product.store == "Compragamer":
            scraper = CompragamerScraper(product.url)
        
        if scraper:
            try:
                scraped_data = await scraper.scrape()
                db_manager.add_price_entry(
                    product_id=product.id,
                    price=scraped_data['price'],
                    is_out_of_stock=scraped_data['is_out_of_stock']
                )
                print(f"✅ Actualizado: ${scraped_data['price']:,.2f}")
            except Exception as e:
                print(f"❌ Error en {product.name}: {e}")
    
    print("Actualización completa.")

if __name__ == "__main__":
    asyncio.run(update_all_prices())
