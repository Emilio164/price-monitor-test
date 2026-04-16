import asyncio
import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), "src"))

from scrapers.fullh4rd_scraper import FullH4rdScraper

async def test_url(url, label):
    print(f"\n--- Testing {label} ---")
    print(f"URL: {url}")
    scraper = FullH4rdScraper(url)
    try:
        result = await scraper.scrape()
        print("Scrape Result:")
        for k, v in result.items():
            print(f"  {k}: {v}")
    except Exception as e:
        print(f"Error during scrape: {e}")

async def main():
    # 1. Con stock en web y local
    url_1 = "https://fullh4rd.com.ar/prod/25029/gabinete-thermaltake-s200-tg-4fan-argb-black"
    await test_url(url_1, "1. Stock en web y local")

    # 2. Con stock en web y sin stock en local
    url_2 = "https://fullh4rd.com.ar/prod/13007/mouse-logitech-g703-lightspeed-wireless-910-005639"
    await test_url(url_2, "2. Stock en web, sin stock en local")

    # 3. No tiene la separación de web y local, los tiene juntos ("STOCK ALTO")
    url_3 = "https://fullh4rd.com.ar/prod/28211/auricular-qbox-h039-usb-jack-35-y-3-pines-gamer-call-center-celular-h390-h110"
    await test_url(url_3, "3. Stock Alto (Juntos)")

    # 4. Sin stock
    url_4 = "https://fullh4rd.com.ar/prod/28648/mouse-gamer-wireless-logitech-g-pro-x-superlight-2-white-910-006637"
    await test_url(url_4, "4. Sin stock")

if __name__ == "__main__":
    asyncio.run(main())
