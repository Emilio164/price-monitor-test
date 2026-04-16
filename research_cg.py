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
        url = "https://compragamer.com/producto/Disco_S_lido_SSD_M_2_Kingston_1TB_NV3_6000MB_s_NVMe_PCI_E_Gen4_x4_16872?cate=81&filtros=175:M2,874:NVMe&sort=lower_price"
        
        print(f"Navegando a {url}...")
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            # Esperar un poco más para que Angular termine de renderizar
            await asyncio.sleep(5)
            content = await page.content()
            with open("compragamer_raw.html", "w", encoding="utf-8") as f:
                f.write(content)
            print("HTML guardado en compragamer_raw.html")
            
            # Captura de pantalla para verificar visualmente si cargó el precio
            await page.screenshot(path="compragamer_check.png")
            print("Captura de pantalla guardada como compragamer_check.png")
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
