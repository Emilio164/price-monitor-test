from abc import ABC, abstractmethod
import re
import os
import datetime
from typing import Dict, Any

class ScrapingBlockException(Exception):
    """Excepción lanzada cuando se detecta un bloqueo por parte del sitio."""
    pass

class BaseScraper(ABC):
    def __init__(self, url: str):
        self.url = url
        self.store_name = "Base"

    def save_debug_html(self, content: str, suffix: str = "error"):
        """
        Guarda el HTML de la página para depuración.
        """
        try:
            debug_dir = os.path.join(os.getcwd(), "logs", "debug_html")
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.store_name}_{suffix}_{timestamp}.html"
            filepath = os.path.join(debug_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📄 HTML de depuración guardado en: {filepath}")
        except Exception as e:
            print(f"⚠️ No se pudo guardar el HTML de depuración: {e}")

    def check_for_blocks(self, content: str, status: int = 200):
        """
        Verifica si el contenido o el estado indican un bloqueo.
        """
        # 1. Verificar códigos de estado HTTP
        if status in [403, 429]:
            raise ScrapingBlockException(f"Acceso denegado (Status {status}) en {self.store_name}")

        # 2. Verificar palabras clave de bloqueo en el HTML (case-insensitive)
        block_keywords = [
            "captcha", 
            "verify you are human", 
            "access denied", 
            "blocked", 
            "challenge-running",
            "checking your browser",
            "permiso denegado"
        ]
        
        content_lower = content.lower()
        for kw in block_keywords:
            if kw in content_lower:
                raise ScrapingBlockException(f"Bloqueo detectado: '{kw}' en {self.store_name}")

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
