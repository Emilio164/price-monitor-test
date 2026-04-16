import unittest
import sys
import os

# Añadir el path para importar desde src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.scrapers.fullh4rd_scraper import FullH4rdScraper
from src.scrapers.compragamer_scraper import CompragamerScraper
from src.logic.dolar_utils import get_dolar_blue

class TestPriceMonitorLogic(unittest.TestCase):

    def test_fullh4rd_price_cleaning(self):
        scraper = FullH4rdScraper("http://test.com")
        self.assertEqual(scraper._clean_price("$ 1.250,50"), 1250.50)
        self.assertEqual(scraper._clean_price("1.250"), 1250.00)
        self.assertEqual(scraper._clean_price("0"), 0.0)

    def test_compragamer_price_cleaning(self):
        scraper = CompragamerScraper("http://test.com")
        # Compragamer usa puntos para miles y no suele mostrar decimales en el main span
        self.assertEqual(scraper._clean_price("261.700"), 261700.0)
        self.assertEqual(scraper._clean_price("2.313.956"), 2313956.0)

    def test_dolar_utils_structure(self):
        data = get_dolar_blue()
        if data: # Si hay internet y la API responde
            self.assertIn('buy', data)
            self.assertIn('sell', data)
            self.assertIsInstance(data['buy'], (int, float))

if __name__ == '__main__':
    unittest.main()
