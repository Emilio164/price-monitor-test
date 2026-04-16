import asyncio
import random
import sys
import os

# Asegurar que la raíz del proyecto esté en el path para las importaciones de 'src'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db_manager import DatabaseManager
from src.scrapers.fullh4rd_scraper import FullH4rdScraper
from src.scrapers.compragamer_scraper import CompragamerScraper
from src.logic.notifications import send_discord_alert

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
                # Obtener precio anterior antes de actualizar
                curr_before, prev_before = db_manager.get_trend_data(product.id)
                
                scraped_data = await scraper.scrape()
                new_price = scraped_data['price']
                
                db_manager.add_price_entry(
                    product_id=product.id,
                    price=new_price,
                    is_out_of_stock=scraped_data['is_out_of_stock']
                )
                print(f"✅ Actualizado: ${new_price:,.2f}")

                # Verificar si hay que enviar alerta a Discord (mínimo 2% de rebaja)
                if curr_before > 0 and new_price < curr_before:
                    diff_percent = ((curr_before - new_price) / curr_before) * 100
                    if diff_percent >= 2.0:
                        send_discord_alert(
                            product_name=product.name,
                            store=product.store,
                            old_price=curr_before,
                            new_price=new_price,
                            url=product.url
                        )
            except Exception as e:
                print(f"❌ Error en {product.name}: {e}")
    
    print("Actualización completa.")

if __name__ == "__main__":
    asyncio.run(update_all_prices())
