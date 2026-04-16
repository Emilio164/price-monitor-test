from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
        self.store_name = "Base"

    @abstractmethod
    async def scrape(self) -> Dict[str, Any]:
        """
        Scrapes the product page and returns a dictionary with:
        {
            'name': str,
            'price': float,
            'is_out_of_stock': bool,
            'store': str,
            'url': str
        }
        """
        pass
