import asyncio
import importlib.util
import sys
import os

async def test_scraper(scraper_path, url):
    """
    Carga dinámicamente un scraper y lo prueba con una URL.
    Uso: python test_new_scraper.py <ruta_del_archivo> <url>
    """
    module_name = os.path.basename(scraper_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, scraper_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    # Encuentra la primera clase que herede de BaseScraper
    scraper_class = None
    for item in dir(module):
        obj = getattr(module, item)
        if isinstance(obj, type) and item != "BaseScraper" and "Scraper" in item:
            scraper_class = obj
            break
            
    if not scraper_class:
        print("❌ No se encontró una clase Scraper en el archivo.")
        return

    print(f"--- Probando {scraper_class.__name__} ---")
    scraper = scraper_class(url)
    try:
        data = await scraper.scrape()
        print(f"✅ Éxito:")
        print(f"  Nombre: {data['name']}")
        print(f"  Precio: ${data['price']:,.2f}")
        print(f"  Stock: {'Agotado' if data['is_out_of_stock'] else 'En Stock'}")
    except Exception as e:
        print(f"❌ Falló el scraping: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python test_new_scraper.py <ruta_scraper> <url>")
    else:
        asyncio.run(test_scraper(sys.argv[1], sys.argv[2]))
