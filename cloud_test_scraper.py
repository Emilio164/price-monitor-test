import asyncio
from playwright.async_api import async_playwright
import sys

async def check_site(name, url):
    print(f"Probando {name}...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            )
            page = await context.new_page()
            
            response = await page.goto(url, wait_until="networkidle", timeout=60000)
            
            if response.status == 200:
                print(f"✅ {name}: CONEXIÓN EXITOSA (Status 200)")
                # Verificar si el contenido no es un captcha
                content = await page.content()
                if "captcha" in content.lower() or "cloudflare" in content.lower():
                    print(f"⚠️ {name}: ¡Detectado CAPTCHA o Cloudflare!")
                else:
                    print(f"✨ {name}: El contenido parece accesible.")
            else:
                print(f"❌ {name}: ERROR Status {response.status}")
            
            await browser.close()
        except Exception as e:
            print(f"❌ {name}: FALLÓ la conexión. Error: {e}")

async def main():
    sites = [
        ("FullH4rd", "https://www.fullh4rd.com.ar/"),
        ("Compragamer", "https://compragamer.com/")
    ]
    for name, url in sites:
        await check_site(name, url)

if __name__ == "__main__":
    asyncio.run(main())
