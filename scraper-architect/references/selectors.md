# Selectores E-commerce Comunes

## Títulos del Producto
*   `h1` (estándar)
*   `.product-name`
*   `.product-title`

## Precios
*   `.price-main`
*   `.price-regular`
*   `.product-price-actual`
*   `[itemprop="price"]`

## Stock e Inventario
*   **Compragamer**: Busca elementos que digan "Añadir al carrito" vs "Agotado".
*   **FullH4rd**: Busca clases como `fa-check-circle` (con stock) o `fa-times-circle` (sin stock).
*   **General**: Busca cadenas de texto como "Sin Stock", "Out of stock", "Producto no disponible".

## Tip para Sitios Dinámicos (como Compragamer)
Compragamer es una SPA (Single Page Application). Usa `page.wait_for_selector()` para esperar a que los datos de precio se carguen mediante sus APIs internas antes de intentar extraerlos.
