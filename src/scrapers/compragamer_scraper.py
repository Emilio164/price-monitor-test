import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, ScrapingBlockException
import re
import os
import random

class CompragamerScraper(BaseScraper):
    def __init__(self, url: str, user_agent: str = None):
        super().__init__(url, user_agent)
        self.store_name = "Compragamer"

    async def scrape(self) -> dict:
        async with async_playwright() as p:
            is_ci = os.environ.get("GITHUB_ACTIONS") == "true"
            browser = await p.chromium.launch(headless=is_ci)
            
            # Usar un contexto limpio sin headers extraños que delaten
            context = await browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            try:
                # 1. Espera inicial corta
                await asyncio.sleep(random.uniform(2.0, 4.0))
                
                # 2. Navegación directa
                response = await page.goto(self.url, wait_until="load", timeout=60000)
                
                # 3. Pausa para carga de SPA
                await asyncio.sleep(5)
                
                # Verificación de bloqueo básica
                content = await page.content()
                status = response.status if response else 200
                self.check_for_blocks(content, status)

                # Intentar obtener el precio
                # Compragamer usa clases dinámicas, probamos selectores conocidos
                price_text = "0"
                
                # Selector principal de precio
                price_elements = await page.query_selector_all(".tw-text-price")
                if not price_elements:
                    price_elements = await page.query_selector_all("span.tw\\:text-price")
                
                if price_elements:
                    for el in price_elements:
                        txt = await el.inner_text()
                        if txt and any(c.isdigit() for c in txt):
                            price_text = txt
                            break
                
                # Si fallan los selectores, intentamos por texto en el body
                if price_text == "0":
                    body_text = await page.inner_text("body")
                    match = re.search(r'(\d{1,3}(\.\d{3})+)', body_text)
                    if match:
                        price_text = match.group(0)

                name_h1 = await page.query_selector("h1")
                name = await name_h1.inner_text() if name_h1 else "Unknown Product"
                name = name.replace("content_copy", "").replace("keyboard_backspace", "").strip()
                
                # Stock
                page_content_text = (await page.inner_text("body")).upper()
                is_out_of_stock = not ("STOCK DISPONIBLE" in page_content_text or "AÑADIR AL CARRITO" in page_content_text)

                price = self._clean_price(price_text)
                if price == 0:
                    is_out_of_stock = True
                
                return {
                    'name': name,
                    'price': price,
                    'is_out_of_stock': is_out_of_stock,
                    'store': self.store_name,
                    'url': self.url
                }

            except ScrapingBlockException as be:
                raise be
            except Exception as e:
                # Si falla, guardar captura para ver qué pasó
                try:
                    c = await page.content()
                    self.save_debug_html(c, "error_simple")
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
