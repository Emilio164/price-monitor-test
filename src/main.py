import streamlit as st
import sys
import os
import asyncio
import nest_asyncio
import pandas as pd
import random
import subprocess # Para instalar Playwright automáticamente en la nube

# --- Playwright Auto-Install for Cloud ---
def install_playwright():
    """Attempts to install playwright browsers if they are missing."""
    try:
        import playwright
    except ImportError:
        return # requirements.txt will handle this later
        
    try:
        # Check if browsers are already installed
        # This is a light-weight check, if it fails, we install
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Error installing playwright browsers: {e}")

# This runs once on app load
if os.environ.get("DATABASE_URL"): # Simple check to see if we are in Cloud/Production
    with st.spinner("Initializing Cloud Environment (Playwright)... This may take a minute."):
        install_playwright()

from database.db_manager import DatabaseManager
from scrapers.fullh4rd_scraper import FullH4rdScraper
from scrapers.compragamer_scraper import CompragamerScraper
from scrapers.diamond_scraper import DiamondScraper
from logic.dolar_utils import get_dolar_blue

# Apply nest_asyncio to allow nested loops in Streamlit
nest_asyncio.apply()

# Configure asyncio for Windows sub-processes
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- Configuration ---
# Lista de User-Agents COHERENTES (Chrome sobre Windows) para evitar detección
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Diccionario de mapeo para escalabilidad: Dominio -> Clase de Scraper
SCRAPER_MAPPING = {
    "fullh4rd.com.ar": FullH4rdScraper,
    "compragamer.com": CompragamerScraper,
    "diamondcomputacion.com.ar": DiamondScraper
}

# Use session state for managing scraped data to avoid re-scraping on every interaction
if 'scraped_product' not in st.session_state:
    st.session_state.scraped_product = None
if 'tracked_products' not in st.session_state:
    st.session_state.tracked_products = []
if 'dolar_blue_data' not in st.session_state:
    st.session_state.dolar_blue_data = None

# --- Database Initialization ---
db_manager = DatabaseManager()
db_manager.init_db() # Ensure tables are created

# --- Helper functions ---
def run_scraper(url):
    if not url:
        st.error("Por favor, ingresa una URL.")
        return None
    
    # Lógica escalable: Buscar el scraper adecuado según el dominio en la URL
    scraper_class = None
    for domain, clazz in SCRAPER_MAPPING.items():
        if domain in url:
            scraper_class = clazz
            break
            
    if not scraper_class:
        st.warning("Actualmente, solo se admiten URLs de FullH4rd, Compragamer y DiamondSystem.")
        return None

    try:
        # Usar un User-Agent aleatorio también al agregar manualmente
        ua = random.choice(USER_AGENTS)
        scraper = scraper_class(url, user_agent=ua)
        scraped_data = asyncio.run(scraper.scrape())
        st.session_state.scraped_product = scraped_data
        st.rerun()
    except Exception as e:
        st.error(f"Error al analizar la URL: {e}")
        return None

def save_to_db(product_data, group_name, category):
    try:
        # 1. Add/Get product
        new_prod = db_manager.add_product(
            name=product_data['name'],
            url=product_data['url'],
            store=product_data['store'],
            group_name=group_name,
            category=category
        )
        # 2. Add price entry
        db_manager.add_price_entry(
            product_id=new_prod.id,
            price=product_data['price'],
            is_out_of_stock=product_data['is_out_of_stock']
        )
        return True
    except Exception as e:
        st.error(f"Error saving to database: {e}")
        return False

async def update_all_prices():
    products = db_manager.get_all_products()
    if not products:
        st.info("No products to update.")
        return

    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, product in enumerate(products):
        # Human-like delay before scraping each product (except the first one)
        if i > 0:
            delay = random.uniform(2.0, 5.0)
            status_text.text(f"Waiting {delay:.1f}s before updating {product.name} to avoid rate limiting...")
            await asyncio.sleep(delay)
        
        status_text.text(f"Updating {product.name} ({product.store})...")
        
        scraper = None
        if product.store == "FullH4rd":
            scraper = FullH4rdScraper(product.url)
        elif product.store == "Compragamer":
            scraper = CompragamerScraper(product.url)
        
        if scraper:
            try:
                scraped_data = await scraper.scrape()
                db_manager.add_price_entry(
                    product_id=product.id,
                    price=scraped_data['price'],
                    is_out_of_stock=scraped_data['is_out_of_stock']
                )
            except Exception as e:
                st.error(f"Failed to update {product.name}: {e}")
        
        progress_bar.progress((i + 1) / len(products))
    
    status_text.text("Update complete!")
    st.rerun()

# --- Fetch Dólar Blue data ---
def fetch_dolar_data():
    if st.session_state.dolar_blue_data is None:
        dolar_data = get_dolar_blue()
        if dolar_data:
            st.session_state.dolar_blue_data = dolar_data
        else:
            st.warning("Could not fetch Dólar Blue data.")

fetch_dolar_data() # Fetch on load


# --- Streamlit App Layout ---
st.set_page_config(page_title="Price Monitor", layout="wide")

st.title("🔍 Multi-Site Price Monitor")

# --- Sidebar Navigation ---
st.sidebar.title("Navegación")
page = st.sidebar.radio("Ir a", ["Panel de Control", "Agregar Producto", "Historial de Precios"])

# --- Dólar Blue Display ---
if st.session_state.dolar_blue_data:
    dolar_info = st.session_state.dolar_blue_data
    st.sidebar.markdown(f"---")
    st.sidebar.subheader("🇦🇷 Dólar Blue")
    st.sidebar.metric("Compra", f"${dolar_info.get('buy', 'N/A'):,.2f}")
    st.sidebar.metric("Venta", f"${dolar_info.get('sell', 'N/A'):,.2f}")
    st.sidebar.metric("Promedio", f"${dolar_info.get('avg', 'N/A'):,.2f}")
else:
    st.sidebar.markdown(f"---")
    st.sidebar.subheader("🇦🇷 Dólar Blue")
    st.sidebar.warning("Datos del Dólar Blue no disponibles.")


# --- Page Content ---
if page == "Panel de Control":
    st.header("📊 Productos Monitoreados")
    
    # --- Quick Filters ---
    st.subheader("Filtros Rápidos")
    
    # Inicializar estado de filtro si no existe
    if 'active_filter' not in st.session_state:
        st.session_state.active_filter = "Todos"
        
    col_f1, col_f2, col_f3, col_empty = st.columns([1, 1, 1, 1])
    
    # Usar botones que cambian el estado
    if col_f1.button("🏠 Todos", use_container_width=True, type="primary" if st.session_state.active_filter == "Todos" else "secondary"):
        st.session_state.active_filter = "Todos"
        st.rerun()
    if col_f2.button("↑ Subió de precio", use_container_width=True, type="primary" if st.session_state.active_filter == "Subio" else "secondary"):
        st.session_state.active_filter = "Subio"
        st.rerun()
    if col_f3.button("↓ Bajó de precio", use_container_width=True, type="primary" if st.session_state.active_filter == "Bajo" else "secondary"):
        st.session_state.active_filter = "Bajo"
        st.rerun()

    filter_choice = st.session_state.active_filter

    col_header, col_btn = st.columns([3, 0.5])
    with col_btn:
        if st.button("🔄", use_container_width=True, help="Actualizar todos los precios"):
            asyncio.run(update_all_prices())

    # Load products from DB
    tracked_products = db_manager.get_all_products()
    
    if not tracked_products:
        st.info("Aún no hay productos monitoreados. Ve a 'Agregar Producto' para empezar.")
    else:
        # Filtrado de productos según selección
        display_list = []
        for prod in tracked_products:
            curr, prev = db_manager.get_trend_data(prod.id)
            median = db_manager.get_median_price(prod.id)
            
            # Lógica de estados para filtros
            has_up_trend = (prev > 0 and curr > prev)
            has_down_trend = (prev > 0 and curr < prev)
            
            # Lógica de indicadores visuales (se mantienen para info)
            is_min = prod.last_price <= prod.min_price if prod.min_price else False
            is_inflated = (prod.last_price / median > 1.10) if median > 0 else False
            is_opportunity = (prod.last_price < median * 0.95) if median > 0 else False
            
            # Aplicar filtro
            if filter_choice == "Todos":
                display_list.append((prod, curr, prev, median, is_min, is_inflated, is_opportunity))
            elif filter_choice == "Subio" and has_up_trend:
                display_list.append((prod, curr, prev, median, is_min, is_inflated, is_opportunity))
            elif filter_choice == "Bajo" and has_down_trend:
                display_list.append((prod, curr, prev, median, is_min, is_inflated, is_opportunity))

        if not display_list:
            st.warning(f"No hay productos que coincidan con el filtro seleccionado.")
        else:
            # Eliminado: st.subheader(f"Mostrando: {filter_choice}")
            st.divider()

            # Organizar datos por Categoría -> Grupo
            categories = sorted(list(set([x[0].category for x in display_list if x[0].category])))
            
            for cat in categories:
                st.header(f"📂 {cat}")
                cat_items = [x for x in display_list if x[0].category == cat]
                
                # Agrupar por Nombre de Grupo dentro de la categoría
                groups = sorted(list(set([x[0].group_name for x in cat_items if x[0].group_name])))
                
                for group in groups:
                    with st.expander(f"📦 {group}", expanded=True):
                        group_items = [x for x in cat_items if x[0].group_name == group]
                        
                        # Headers de la tabla interna
                        h1, h2, h3, h4, h5 = st.columns([2, 1, 1, 1, 0.5])
                        h1.write("**Tienda / Enlace**")
                        h2.write("**Mínimo**")
                        h3.write("**Precio Actual**")
                        h4.write("**Análisis**")
                        h5.write("")
                        st.divider()

                        for prod, curr, prev, median, is_min, is_inflated, is_opportunity in group_items:
                            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 0.5])
                            
                            with col1:
                                st.write(f"**{prod.store}**")
                                st.caption(f"[Ir al sitio]({prod.url})")
                                st.caption(f"_{prod.name}_")
                            
                            with col2:
                                st.write(f"${prod.min_price:,.2f}" if prod.min_price else "N/A")
                                if is_min:
                                    st.markdown(":sparkles: **MÍNIMO**")
                            
                            with col3:
                                trend_icon = "-"
                                trend_color = "gray"
                                trend_details = ""
                                if prev > 0:
                                    if curr < prev:
                                        trend_icon = "↓"
                                        trend_color = "green"
                                        diff = prev - curr
                                        percent = (diff / prev) * 100
                                        trend_details = f"<br><span style='color:green; font-size: 14px;'>📉 -${diff:,.2f} (-{percent:.1f}%)</span>"
                                    elif curr > prev:
                                        trend_icon = "↑"
                                        trend_color = "red"
                                        diff = curr - prev
                                        percent = (diff / prev) * 100
                                        trend_details = f"<br><span style='color:red; font-size: 14px;'>📈 +${diff:,.2f} (+{percent:.1f}%)</span>"
                                
                                st.markdown(f"#### ${curr:,.2f}")
                                st.markdown(f"<span style='color:{trend_color}; font-size: 18px;'>{trend_icon}</span> (vs anterior){trend_details}", unsafe_allow_html=True)
                            
                            with col4:
                                if is_inflated:
                                    st.error("🚩 INFLADO")
                                elif is_opportunity:
                                    st.success("✅ OFERTA")
                                else:
                                    st.write("Estable")
                                
                                if median > 0:
                                    st.caption(f"Mediana: ${median:,.2f}")
                            
                            with col5:
                                if st.button("🗑️", key=f"del_{prod.id}", help="Eliminar Producto"):
                                    if db_manager.delete_product(prod.id):
                                        st.success(f"Eliminado")
                                        st.rerun()
                            st.divider()
        
elif page == "Agregar Producto":
    st.header("➕ Agregar Nuevo Producto para Monitorear")
    url = st.text_input("URL del Producto", key="product_url_input")
    
    if st.button("Analizar URL", key="analyze_url_button"):
        if url:
            st.info(f"Analizando: {url}")
            run_scraper(url) 

    # Display scraped product details after analysis
    if st.session_state.scraped_product:
        product = st.session_state.scraped_product
        st.subheader("Detalles del Producto:")
        
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Nombre:** {product.get('name', 'N/A')}")
            st.write(f"**Precio:** ${product.get('price', 0.0):,.2f}")
            st.write(f"**Tienda:** {product.get('store', 'N/A')}")
        
        with col2:
            # Obtener grupos y categorías existentes para sugerencias
            existing_products = db_manager.get_all_products()
            existing_groups = sorted(list(set([p.group_name for p in existing_products if p.group_name])))
            existing_cats = sorted(list(set([p.category for p in existing_products if p.category])))
            
            group_name = st.selectbox("Asignar a Grupo (Existente)", options=["Nuevo Grupo..."] + existing_groups)
            if group_name == "Nuevo Grupo...":
                group_name = st.text_input("Nombre del Nuevo Grupo", value=product.get('name', ''))
            
            category = st.selectbox("Categoría (Existente)", options=["Nueva Categoría..."] + existing_cats)
            if category == "Nueva Categoría...":
                category = st.text_input("Nombre de la Nueva Categoría", value="General")

        # Add to tracked products logic
        if st.button("Confirmar e Iniciar Monitoreo", key="save_to_db_button"):
            if save_to_db(product, group_name, category):
                st.success(f"¡'{group_name}' ({product.get('store')}) ahora está siendo monitoreado!")
                st.session_state.scraped_product = None
                st.rerun()
        
        if st.button("Cancelar", key="clear_scraped_product"):
            st.session_state.scraped_product = None
            st.rerun()

elif page == "Historial de Precios":
    st.header("📈 Historial de Precios")
    
    # Load products for selection
    products = db_manager.get_all_products()
    
    if not products:
        st.info("Aún no hay productos monitoreados. Agrega algunos primero para ver su historial.")
    else:
        # Create a dictionary for selection (name -> id)
        product_options = {f"{p.name} ({p.store})": p.id for p in products}
        selected_product_name = st.selectbox("Selecciona un producto para ver su historial:", options=list(product_options.keys()))
        
        if selected_product_name:
            product_id = product_options[selected_product_name]
            history = db_manager.get_product_history(product_id)
            
            if not history:
                st.warning("No se encontró historial de precios para este producto.")
            else:
                # Prepare data for the chart using pandas
                data = {
                    "Fecha": [h.timestamp for h in history],
                    "Precio": [h.price for h in history]
                }
                df = pd.DataFrame(data)
                df.set_index("Fecha", inplace=True)
                
                # Summary metrics
                last_price = history[-1].price
                min_price = min(h.price for h in history if h.price > 0)
                
                col1, col2 = st.columns(2)
                col1.metric("Precio Actual", f"${last_price:,.2f}")
                col2.metric("Mínimo Histórico", f"${min_price:,.2f}")
                
                # Plotting
                st.subheader("Evolución de Precio")
                st.line_chart(df)
                
                # Show raw data in an expander
                with st.expander("Ver Datos Crudos del Historial"):
                    st.table(df)
