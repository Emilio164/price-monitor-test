import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, ScrapingBlockException
import re
import os
import random
import json

class DiamondScraper(BaseScraper):
    def __init__(self, url: str, user_agent: str = None):
        super().__init__(url, user_agent)
        self.store_name = "DiamondSystem"

    async def scrape(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Setup context with enhanced stealth
            viewport_width = random.randint(1280, 1920)
            viewport_height = random.randint(720, 1080)
            
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': viewport_width, 'height': viewport_height},
                extra_http_headers={
                    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.google.com/search?q=" + self.store_name,
                    "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "cross-site",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            page = await context.new_page()

            # --- SCRIPT ANTI-DETECCIÓN ---
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            # -----------------------------

            try:
                # 1. Delay humano
                await asyncio.sleep(random.uniform(3.0, 7.0))
                
                # 2. Navegar
                response = await page.goto(self.url, wait_until="commit", timeout=60000)
                
                # Espera extra para Cloudflare
                await asyncio.sleep(random.uniform(5.0, 8.0))
                
                # --- NUEVA DETECCIÓN DE BLOQUEOS ---
                content = await page.content()
                status = response.status if response else 200
                self.check_for_blocks(content, status)
                # ----------------------------------

                # Simular interacción humana avanzada
                await asyncio.sleep(random.uniform(1.5, 3.5))
                for _ in range(random.randint(1, 3)):
                    await page.mouse.move(random.randint(200, 700), random.randint(200, 500))
                    await asyncio.sleep(random.uniform(0.3, 0.8))

                # 3. Scroll y espera
                await page.mouse.wheel(0, random.randint(300, 600))
                await asyncio.sleep(2)
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

            except ScrapingBlockException as be:
                print(f"🛑 BLOQUEO en {self.store_name}: {be}")
                try:
                    content = await page.content()
                    self.save_debug_html(content, "blocked")
                except: pass
                raise be
            except Exception as e:
                print(f"❌ ERROR en {self.store_name}: {e}")
                try:
                    content = await page.content()
                    self.save_debug_html(content, "error")
                except: pass
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
