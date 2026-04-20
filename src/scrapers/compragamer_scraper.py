import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, ScrapingBlockException
import re
import os
import random

class CompragamerScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)
        self.store_name = "Compragamer"

    async def scrape(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            # Configuración de contexto con sigilo mejorado
            viewport_width = random.randint(1280, 1920)
            viewport_height = random.randint(720, 1080)
            
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                viewport={'width': viewport_width, 'height': viewport_height},
                extra_http_headers={
                    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.google.com/",
                    "Sec-Ch-Ua": '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
                    "Sec-Ch-Ua-Mobile": "?0",
                    "Sec-Ch-Ua-Platform": '"Windows"',
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "same-origin",
                    "Sec-Fetch-User": "?1",
                    "Upgrade-Insecure-Requests": "1"
                }
            )
            page = await context.new_page()

            try:
                # 1. Simular reacción humana: pequeña espera aleatoria antes de navegar
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
                # 2. Navegar con timeout extendido para sitios lentos
                response = await page.goto(self.url, wait_until="domcontentloaded", timeout=60000)
                
                # --- NUEVA DETECCIÓN DE BLOQUEOS ---
                content = await page.content()
                status = response.status if response else 200
                self.check_for_blocks(content, status)
                # ----------------------------------

                # 3. Simular lectura: pequeño scroll para activar contenido dinámico
                await asyncio.sleep(random.uniform(2.0, 4.0)) # Espera a que cargue el JS
                await page.mouse.wheel(0, random.randint(300, 700))
                await asyncio.sleep(random.uniform(1.0, 2.0))
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(random.uniform(1.0, 2.0))
                
                # En Compragamer el precio suele estar cerca de un texto que dice "Precio Especial"
                price_text = "0"
                try:
                    # Esperamos a que la página cargue algo de contenido
                    await page.wait_for_load_state("networkidle")
                    await asyncio.sleep(3) # Espera extra para Angular
                    
                    # Intentamos buscar el precio que esté dentro del componente de precio
                    # Compragamer usa clases dinámicas, pero el texto es constante
                    price_elements = await page.query_selector_all("span.tw\\:text-price")
                    if not price_elements:
                         # Selector alternativo buscando por la clase de color de precio
                         price_elements = await page.query_selector_all(".tw-text-price")
                    
                    if price_elements:
                        for el in price_elements:
                            txt = await el.inner_text()
                            if txt and any(c.isdigit() for c in txt):
                                price_text = txt
                                break
                    else:
                        # Si fallan los selectores, buscamos el primer número grande en el cuerpo
                        body_text = await page.inner_text("body")
                        # Buscar patrón de precio tipo 261.700
                        match = re.search(r'(\d{1,3}(\.\d{3})+)', body_text)
                        if match:
                            price_text = match.group(0)
                    
                    name_h1 = await page.query_selector("h1")
                    name = await name_h1.inner_text() if name_h1 else "Unknown Product"
                    name = name.replace("content_copy", "").replace("keyboard_backspace", "").strip()
                    
                    # Verificación de stock directamente en el texto de la página renderizada
                    page_content_text = await page.inner_text("body")
                    page_content_text = page_content_text.upper()
                    
                    is_out_of_stock = True
                    if "STOCK DISPONIBLE" in page_content_text or "AÑADIR AL CARRITO" in page_content_text:
                        is_out_of_stock = False
                except Exception as e:
                    print(f"Advertencia: Falló captura directa de Playwright ({e}). Usando BeautifulSoup como backup.")
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    name_elem = soup.find('h1')
                    name = name_elem.get_text(strip=True).replace("content_copykeyboard_backspace", "").strip() if name_elem else "Unknown Product"
                    price_elem = soup.select_one(price_selector) or soup.select_one(".tw-text-price")
                    price_text = price_elem.text.strip() if price_elem else "0"
                    
                    page_text = soup.get_text().upper()
                    is_out_of_stock = not ("STOCK DISPONIBLE" in page_text or "AÑADIR AL CARRITO" in page_text)

                price = self._clean_price(price_text)
                
                # Validación de seguridad: si el precio es 0, marcamos como sin stock
                if price == 0.0:
                    is_out_of_stock = True
                
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
        # Compragamer usa formato: 261.700 (punto para miles, sin decimales usualmente)
        clean = re.sub(r'[^\d]', '', price_str)
        try:
            return float(clean)
        except ValueError:
            return 0.0
