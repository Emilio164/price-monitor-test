import asyncio
import random
import sys
import os

# Asegurar que la raíz del proyecto esté en el path para las importaciones de 'src'
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.database.db_manager import DatabaseManager
from src.scrapers.fullh4rd_scraper import FullH4rdScraper
from src.scrapers.compragamer_scraper import CompragamerScraper
from src.scrapers.diamond_scraper import DiamondScraper # Importación arriba
from src.logic.notifications import send_discord_alert

# --- CONFIGURACIÓN ESCALABLE ---
# Si agregas una tienda nueva, solo la sumas aquí:
SCRAPER_CLASSES = {
    "FullH4rd": FullH4rdScraper,
    "Compragamer": CompragamerScraper,
    "DiamondSystem": DiamondScraper,
    # "NuevaTienda": NuevaTiendaScraper,
}

# Lista de User-Agents COHERENTES (Chrome sobre Windows) para evitar detección
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

async def update_all_prices():
    db_manager = DatabaseManager()
    db_manager.init_db()
    
    products = db_manager.get_all_products()
    if not products:
        print("No hay productos para actualizar.")
        return

    # 1. Delay inicial aleatorio (0 a 30 min)
    initial_delay = random.uniform(0, 1800)
    print(f"⏰ Espera inicial aleatoria: {initial_delay/60:.1f} minutos...")
    await asyncio.sleep(initial_delay)

    # 2. Aleatoriedad de productos
    random.shuffle(products)
    print(f"🚀 Iniciando actualización de {len(products)} productos en orden aleatorio...")
    
    for i, product in enumerate(products):
        if i > 0:
            delay = random.uniform(10.0, 25.0)
            print(f"⏳ Esperando {delay:.1f}s antes del siguiente producto...")
            await asyncio.sleep(delay)
        
        print(f"Procesando: {product.name} ({product.store})...")
        
        # Seleccionar User-Agent aleatorio para este producto
        ua = random.choice(USER_AGENTS)

        # --- LÓGICA ESCALABLE DE SCRAPERS ---
        scraper_class = SCRAPER_CLASSES.get(product.store)
        if not scraper_class:
            print(f"⚠️ No hay scraper configurado para la tienda: {product.store}")
            continue
            
        scraper = scraper_class(product.url, user_agent=ua)
        # ------------------------------------

        success = False
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                # Obtener precio anterior
                curr_before, _ = db_manager.get_trend_data(product.id)

                scraped_data = await scraper.scrape()
                new_price = scraped_data['price']

                # --- NUEVA VALIDACIÓN ANTI-CERO ---
                if new_price <= 0:
                    raise ValueError(f"El precio obtenido es $0.00. Posible carga fallida o bloqueo no detectado.")
                # ----------------------------------

                db_manager.add_price_entry(

                    product_id=product.id,
                    price=new_price,
                    is_out_of_stock=scraped_data['is_out_of_stock']
                )
                print(f"✅ Actualizado: ${new_price:,.2f}")

                # Alerta Discord (mínimo 2% de rebaja)
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
                success = True
                break 
            except Exception as e:
                if attempt < max_retries:
                    wait_retry = random.uniform(15, 30)
                    print(f"⚠️ Intento {attempt + 1} falló para {product.name}. Reintentando en {wait_retry:.1f}s... Error: {e}")
                    await asyncio.sleep(wait_retry)
                else:
                    print(f"❌ Error persistente en {product.name} tras {max_retries} reintentos: {e}")
    
    print("Actualización completa.")

if __name__ == "__main__":
    asyncio.run(update_all_prices())
