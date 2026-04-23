import streamlit as st
import sys
import os
import asyncio
import nest_asyncio
import pandas as pd
import random
import subprocess 

# --- Playwright Auto-Install for Cloud ---
def install_playwright():
    try:
        import playwright
    except ImportError:
        return
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception as e:
        st.error(f"Error al instalar navegadores: {e}")

if os.environ.get("DATABASE_URL"):
    with st.spinner("Iniciando entorno en la nube..."):
        install_playwright()

from database.db_manager import DatabaseManager
from scrapers.fullh4rd_scraper import FullH4rdScraper
from scrapers.compragamer_scraper import CompragamerScraper
from scrapers.diamond_scraper import DiamondScraper
from logic.dolar_utils import get_dolar_blue
from logic.matcher import ProductMatcher

matcher = ProductMatcher()
nest_asyncio.apply()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

SCRAPER_MAPPING = {
    "fullh4rd.com.ar": FullH4rdScraper,
    "compragamer.com": CompragamerScraper,
    "diamondcomputacion.com.ar": DiamondScraper
}

if 'scraped_product' not in st.session_state:
    st.session_state.scraped_product = None
if 'tracked_products' not in st.session_state:
    st.session_state.tracked_products = []
if 'dolar_blue_data' not in st.session_state:
    st.session_state.dolar_blue_data = None
if 'active_filter' not in st.session_state:
    st.session_state.active_filter = "Todos"

db_manager = DatabaseManager()
db_manager.init_db()

# --- Funciones de Ayuda ---
@st.cache_data(ttl=600)
def get_cached_products(currency_mode):
    tracked_products = db_manager.get_all_products()
    processed_list = []
    for prod in tracked_products:
        curr, prev = db_manager.get_trend_data(prod.id)
        median = db_manager.get_median_price(prod.id)
        has_up_trend = (prev > 0 and curr > prev)
        has_down_trend = (prev > 0 and curr < prev)
        is_min = prod.last_price <= prod.min_price if prod.min_price else False
        is_inflated = (prod.last_price / median > 1.10) if median > 0 else False
        is_opportunity = (prod.last_price < median * 0.95) if median > 0 else False
        processed_list.append({
            "prod": prod, "curr": curr, "prev": prev, "median": median,
            "is_min": is_min, "is_inflated": is_inflated, "is_opportunity": is_opportunity,
            "has_up_trend": has_up_trend, "has_down_trend": has_down_trend
        })
    return processed_list

def format_currency(amount, mode, timestamp=None):
    if mode == "Pesos ARS":
        return f"${amount:,.2f}"
    else:
        from datetime import datetime
        target_date = timestamp if timestamp else datetime.utcnow()
        dolar_val = 1000.0
        try:
            dolar_entry = db_manager.get_dolar_on_date(target_date)
            if dolar_entry and dolar_entry.avg > 0:
                dolar_val = dolar_entry.avg
            elif st.session_state.dolar_blue_data:
                dolar_val = st.session_state.dolar_blue_data.get('avg', 1000)
        except:
            pass
        return f"u$s {amount / dolar_val:,.2f}"

def run_scraper(url):
    if not url:
        st.error("Por favor, ingresa una URL.")
        return
    scraper_class = next((clazz for domain, clazz in SCRAPER_MAPPING.items() if domain in url), None)
    if not scraper_class:
        st.warning("Tienda no soportada actualmente.")
        return
    try:
        ua = random.choice(USER_AGENTS)
        scraper = scraper_class(url, user_agent=ua)
        st.session_state.scraped_product = asyncio.run(scraper.scrape())
        st.rerun()
    except Exception as e:
        st.error(f"Error al analizar la URL: {e}")

def save_to_db(product_data, group_name, category):
    try:
        new_prod = db_manager.add_product(
            name=product_data['name'], url=product_data['url'],
            store=product_data['store'], group_name=group_name, category=category
        )
        db_manager.add_price_entry(product_id=new_prod.id, price=product_data['price'], is_out_of_stock=product_data['is_out_of_stock'])
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

async def update_all_prices_manual():
    products = db_manager.get_all_products()
    if not products: return
    progress_bar = st.progress(0)
    status_text = st.empty()
    for i, product in enumerate(products):
        if i > 0: await asyncio.sleep(random.uniform(2, 5))
        status_text.text(f"Actualizando {product.name}...")
        scraper_class = next((clazz for domain, clazz in SCRAPER_MAPPING.items() if domain in product.url or product.store.lower() in clazz.__name__.lower()), None)
        if scraper_class:
            try:
                ua = random.choice(USER_AGENTS)
                scraper = scraper_class(product.url, user_agent=ua)
                data = await scraper.scrape()
                if data['price'] > 0:
                    db_manager.add_price_entry(product.id, data['price'], data['is_out_of_stock'])
            except: pass
        progress_bar.progress((i + 1) / len(products))
    st.cache_data.clear()
    st.rerun()

# --- Carga de Datos ---
if st.session_state.dolar_blue_data is None:
    st.session_state.dolar_blue_data = get_dolar_blue()

# --- UI Layout ---
st.set_page_config(page_title="Price Monitor", layout="wide")
st.title("🔍 Multi-Site Price Monitor")

# --- Sidebar ---
st.sidebar.title("Navegación")
page = st.sidebar.radio("Navegación Principal", ["Panel de Control", "Agregar Producto", "Historial de Precios"], label_visibility="collapsed")
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración")
currency = st.sidebar.radio("Moneda de Visualización", ["Pesos ARS", "Dólar Blue"])

if st.session_state.dolar_blue_data:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🇦🇷 Dólar Blue Hoy")
    st.sidebar.metric("Promedio", f"${st.session_state.dolar_blue_data.get('avg', 0):,.2f}")

# --- Pages ---
if page == "Panel de Control":
    st.header("📊 Productos Monitoreados")
    col_f1, col_f2, col_f3, col_btn = st.columns([1, 1, 1, 0.5])
    if col_f1.button("🏠 Todos", use_container_width=True, type="primary" if st.session_state.active_filter == "Todos" else "secondary"):
        st.session_state.active_filter = "Todos"; st.rerun()
    if col_f2.button("↑ Subió", use_container_width=True, type="primary" if st.session_state.active_filter == "Subio" else "secondary"):
        st.session_state.active_filter = "Subio"; st.rerun()
    if col_f3.button("↓ Bajó", use_container_width=True, type="primary" if st.session_state.active_filter == "Bajo" else "secondary"):
        st.session_state.active_filter = "Bajo"; st.rerun()
    with col_btn:
        if st.button("🔄", use_container_width=True):
            st.cache_data.clear()
            asyncio.run(update_all_prices_manual())

    display_list = [item for item in get_cached_products(currency) if st.session_state.active_filter == "Todos" or (st.session_state.active_filter == "Subio" and item['has_up_trend']) or (st.session_state.active_filter == "Bajo" and item['has_down_trend'])]
    
    if not display_list:
        st.info("No hay productos para mostrar.")
    else:
        st.divider()
        categories = sorted(list(set([x['prod'].category for x in display_list])))
        for cat in categories:
            st.header(f"📂 {cat}")
            cat_items = [x for x in display_list if x['prod'].category == cat]
            groups = sorted(list(set([x['prod'].group_name for x in cat_items])))
            for grp in groups:
                with st.expander(f"📦 {grp}", expanded=True):
                    h1, h2, h3, h4, h5 = st.columns([2, 1, 1, 1, 0.5])
                    h1.write("**Tienda**"); h2.write("**Mínimo**"); h3.write("**Actual**"); h4.write("**Análisis**"); h5.write("")
                    st.markdown("<hr style='margin:0; padding:0;'>", unsafe_allow_html=True)
                    for item in [x for x in cat_items if x['prod'].group_name == grp]:
                        p = item['prod']
                        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1, 0.5])
                        with c1: st.write(f"**{p.store}**"); st.caption(f"[{p.name}]({p.url})")
                        with c2: st.write(format_currency(p.min_price, currency, p.created_at))
                        with c3:
                            st.markdown(f"#### {format_currency(item['curr'], currency)}")
                            if item['prev'] > 0:
                                color = "green" if item['curr'] < item['prev'] else "red"
                                diff = abs(item['curr'] - item['prev'])
                                st.markdown(f"<span style='color:{color};'>{'↓' if item['curr'] < item['prev'] else '↑'} {format_currency(diff, currency)}</span>", unsafe_allow_html=True)
                        with c4:
                            if item['is_inflated']: st.error("🚩 INFLADO")
                            elif item['is_opportunity']: st.success("✅ OFERTA")
                            else: st.write("Estable")
                        with c5:
                            if st.button("🗑️", key=f"del_{p.id}"):
                                if db_manager.delete_product(p.id): st.cache_data.clear(); st.rerun()
                        st.divider()

elif page == "Agregar Producto":
    st.header("➕ Agregar Producto")
    url = st.text_input("URL del Producto")
    if st.button("Analizar URL"): run_scraper(url)
    if st.session_state.scraped_product:
        sp = st.session_state.scraped_product
        st.subheader("Resultado del Análisis:")
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Nombre:** {sp['name']}")
            st.write(f"**Precio:** ${sp['price']:,.2f}")
            st.write(f"**Tienda:** {sp['store']}")
        with col2:
            existing = db_manager.get_all_products()
            ex_groups = sorted(list(set([p.group_name for p in existing])))
            ex_cats = sorted(list(set([p.category for p in existing])))
            
            # Sugerencia de Matching
            suggested_grp = None; suggested_cat = "General"; match_conf = 0
            for p in existing:
                m = matcher.get_similarity_score(sp['name'], p.name)
                if m['is_match'] and m['score'] > match_conf:
                    match_conf = m['score']; suggested_grp = p.group_name; suggested_cat = p.category
            
            if suggested_grp: st.success(f"🔍 Sugerido: {suggested_grp} ({match_conf*100:.0f}%)")
            
            grp_name = st.selectbox("Grupo", ["Nuevo..."] + ex_groups, index=ex_groups.index(suggested_grp)+1 if suggested_grp in ex_groups else 0)
            final_grp = st.text_input("Nombre Grupo", value=suggested_grp if grp_name == "Nuevo..." else grp_name) if grp_name == "Nuevo..." else grp_name
            cat_name = st.selectbox("Categoría", ["Nueva..."] + ex_cats, index=ex_cats.index(suggested_cat)+1 if suggested_cat in ex_cats else 0)
            final_cat = st.text_input("Nombre Categoría", value=suggested_cat if cat_name == "Nueva..." else cat_name) if cat_name == "Nueva..." else cat_name

        if st.button("Confirmar Monitoreo"):
            if save_to_db(sp, final_grp, final_cat):
                st.session_state.scraped_product = None; st.cache_data.clear(); st.rerun()

elif page == "Historial de Precios":
    st.header("📈 Historial")
    prods = db_manager.get_all_products()
    if prods:
        sel_p = st.selectbox("Producto", [f"{p.name} ({p.store})" for p in prods])
        p_obj = next(p for p in prods if f"{p.name} ({p.store})" == sel_p)
        hist = db_manager.get_product_history(p_obj.id)
        if hist:
            df = pd.DataFrame([{"Fecha": h.timestamp, "Precio": h.price} for h in hist]).set_index("Fecha")
            st.line_chart(df)
            with st.expander("Ver Datos"): st.table(df)
