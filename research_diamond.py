import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        url = "https://www.diamondcomputacion.com.ar/ssd-1tb-nvme-kingston-nv3/p"
        
        print(f"Navegando a {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await asyncio.sleep(5) # Espera por JS
            content = await page.content()
            with open("diamond_raw.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("HTML guardado en diamond_raw.html")
            await page.screenshot(path="diamond_check.png")
            print("Captura de pantalla guardada como diamond_check.png")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
