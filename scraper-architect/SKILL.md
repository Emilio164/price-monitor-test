---
name: scraper-architect
description: Guía especializada para la creación y mantenimiento de scrapers de e-commerce en el proyecto Price Monitor. Úsalo cuando necesites agregar un nuevo sitio (Compragamer, Diamond, etc.) o corregir uno existente.
---

# Scraper Architect Skill

Esta skill asegura que todos los scrapers del proyecto `segundo-proyecto` sean consistentes, resilientes y precisos.

## Flujo de Trabajo: Creación de un Nuevo Scraper

1.  **Investigación de Selectores**: Identifica los selectores CSS/HTML para:
    *   Nombre del producto (`h1` usualmente).
    *   Precio (busca clases como `.price`, `.product-price`).
    *   Stock (busca textos como "En stock", "Sin stock", "Agotado" o iconos de check/cross).

2.  **Implementación de la Clase**:
    *   Crea un archivo en `src/scrapers/<sitio>_scraper.py`.
    *   Hereda de `BaseScraper`.
    *   Define `self.store_name` en el `__init__`.
    *   Implementa el método `async def scrape(self)`.

3.  **Patrón de Playwright Estándar**:
    *   Usa `headless=True`.
    *   Configura `User-Agent` y headers para evitar bloqueos.
    *   Usa `wait_until="networkidle"` y un timeout de al menos 60s.

4.  **Sanitización de Datos**:
    *   **Precio**: Usa un método `_clean_price` que maneje el formato argentino (punto para miles, coma para decimales).
    *   **Stock**: Implementa lógica que detecte explícitamente tanto el éxito ("Hay stock") como el fallo ("Agotado").

5.  **Validación**:
    *   Ejecuta el script de prueba de la skill para verificar que los datos extraídos sean correctos.

## Reglas de Oro

*   **No asumas stock**: Si no encuentras el elemento de stock, marca `is_out_of_stock = True` por seguridad.
*   **Manejo de Excepciones**: Siempre usa bloques `try/except/finally` para asegurar que el navegador se cierre (`browser.close()`).
*   **Keyword Filtering**: Verifica si el nombre del producto contiene "Usado", "Outlet" o "Reacondicionado" para reportarlo si es necesario.

## Recursos Disponibles

*   **[selectors.md](references/selectors.md)**: Biblioteca de selectores comunes.
*   **[test_new_scraper.py](scripts/test_new_scraper.py)**: Script para validar un nuevo scraper.
