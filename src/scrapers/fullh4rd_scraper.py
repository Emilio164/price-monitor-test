import asyncio
from playwright.async_api import async_playwright, Playwright, Browser, Page
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
import re
import os
import random

class FullH4rdScraper(BaseScraper):
    def __init__(self, url: str):
        super().__init__(url)
        self.store_name = "FullH4rd"

    async def scrape(self) -> dict:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # Setup context without unsupported trace arguments
            traces_dir = os.path.join(os.getcwd(), "playwright_traces")
            os.makedirs(traces_dir, exist_ok=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                extra_http_headers={
                    "Accept-Language": "es-AR,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Referer": "https://www.google.com/"
                }
            )
            
            page = await context.new_page()

            try:
                # Delay inicial aleatorio para simular reacción humana
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                await page.goto(self.url, wait_until="networkidle", timeout=120000)
                
                # Scroll simulado para activar lazy-loading
                await page.mouse.wheel(0, 500)
                await asyncio.sleep(random.uniform(0.5, 1.5))
                
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                name_elem = soup.find('h1')
                name = name_elem.text.strip() if name_elem else "Unknown Product"
                
                price_elem = soup.select_one('.price-main') or soup.select_one('.price') or soup.select_one('.product-price')
                price_text = price_elem.text.strip() if price_elem else "0"
                price = self._clean_price(price_text)

                is_out_of_stock = True
                check_icon_element = soup.find('i', class_='fa-check-circle', attrs={'aria-hidden': 'true'})
                if check_icon_element:
                    stock_text_container = check_icon_element.find_parent() or check_icon_element.find_next_sibling()
                    if stock_text_container:
                        stock_info_text = stock_text_container.get_text(separator=' ', strip=True).upper()
                        if "STOCK ALTO EN LA WEB" in stock_info_text or "STOCK ALTO" in stock_info_text:
                            is_out_of_stock = False

                if is_out_of_stock:
                    times_icon_element = soup.find('i', class_='fa-times-circle', attrs={'aria-hidden': 'true'})
                    if times_icon_element:
                        no_stock_text_container = times_icon_element.find_parent() or times_icon_element.find_next_sibling()
                        if no_stock_text_container:
                            no_stock_info_text = no_stock_text_container.get_text(separator=' ', strip=True).upper()
                            if "SIN STOCK EN LA WEB" in no_stock_info_text or "SIN STOCK" in no_stock_info_text or "AGOTADO" in no_stock_info_text:
                                is_out_of_stock = True
                            else:
                                is_out_of_stock = True
                
                if price == 0.0 and is_out_of_stock:
                    is_out_of_stock = True
                
                return {
                    'name': name,
                    'price': price,
                    'is_out_of_stock': is_out_of_stock,
                    'store': self.store_name,
                    'url': self.url
                }

            except Exception as e:
                print(f"ERROR: {e}")
                raise e
            finally:
                await context.close()
                await browser.close()

    def _clean_price(self, price_str: str) -> float:
        if not price_str:
            return 0.0
        clean = re.sub(r'[^\d,]', '', price_str)
        if ',' in clean:
            clean = clean.replace('.', '').replace(',', '.')
        else:
            clean = clean.replace('.', '')
            
        try:
            return float(clean)
        except ValueError:
            return 0.0
