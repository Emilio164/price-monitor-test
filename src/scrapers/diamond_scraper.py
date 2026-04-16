import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import re
import os
import random
import json

class DiamondScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)
        self.store_name = "DiamondSystem"

    async def scrape(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.google.com/"
                }
            )
            page = await context.new_page()

            try:
                # 1. Delay humano
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                # 2. Navegar
                await page.goto(self.url, wait_until="networkidle", timeout=60000)
                
                # 3. Scroll y espera
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(2)
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Nombre (H1 como fallback)
                name_elem = soup.find('h1')
                name = name_elem.get_text(strip=True) if name_elem else "Unknown Product"
                
                price = 0.0
                is_out_of_stock = True

                # 4. Extracción vía JSON-LD (Más robusto para Precio y Nombre)
                json_ld_scripts = soup.find_all('script', type='application/ld+json')
                for json_ld in json_ld_scripts:
                    try:
                        data = json.loads(json_ld.string)
                        items = data if isinstance(data, list) else [data]
                        product_data = next((item for item in items if item.get("@type") == "Product"), None)
                        
                        if product_data:
                            offers = product_data.get("offers", {})
                            if isinstance(offers, list): offers = offers[0] if offers else {}
                            
                            if isinstance(offers, dict):
                                price_val = offers.get("lowPrice") or offers.get("price") or 0
                                price = float(price_val)
                                break
                    except:
                        continue

                # 5. Lógica de Stock Mejorada (VTEX Style)
                is_out_of_stock = True
                
                # Búsqueda agresiva: si dice "stock" y NO dice "sin" o "agotado" cerca
                page_text_upper = soup.get_text().upper()
                if "STOCK DISPONIBLE" in page_text_upper or "HAY STOCK" in page_text_upper:
                    is_out_of_stock = False
                elif "AÑADIR AL CARRITO" in page_text_upper or "COMPRAR" in page_text_upper:
                    is_out_of_stock = False
                elif "AGOTADO" not in page_text_upper and "SIN STOCK" not in page_text_upper:
                    # Si no hay mensajes negativos de stock, asumimos que hay (basado en el botón)
                    is_out_of_stock = False

                # Fallback de Precio si el JSON falló
                if price == 0.0:
                    price_elem = soup.select_one('.vtex-product-price-1-x-currencyInteger')
                    if price_elem:
                        price = self._clean_price(price_elem.text)

                return {
                    'name': name,
                    'price': price,
                    'is_out_of_stock': is_out_of_stock,
                    'store': self.store_name,
                    'url': self.url
                }

            except Exception as e:
                print(f"ERROR en DiamondScraper: {e}")
                raise e
            finally:
                await context.close()
                await browser.close()

    def _clean_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0
        clean = re.sub(r'[^\d]', '', price_str)
        try:
            return float(clean)
        except ValueError:
            return 0.0
