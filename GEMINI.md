# GEMINI.md - Project Context

## Project Overview
`segundo-proyecto` is a **Multi-Site Price Monitor (Cloud-Native)** application. Its goal is to track, compare, and notify price changes across Compragamer, FullH4rd, and Diamond Computacion.

**Key Features:**
- **Hybrid Architecture:** Uses Supabase (PostgreSQL) in the cloud and SQLite locally.
- **Automated Scraping:** GitHub Actions updates prices daily at 08:00 AM (ART) automatically.
- **Intelligent Grouping:** Compares the same product across different stores in a unified view.
- **Smart Analysis:** Detects "Inflated Prices" vs "Real Opportunities" using 30-day medians and trend arrows.
- **Ahorro Visual:** Muestra la rebaja exacta en monto fijo ($) y porcentaje (%) frente al último registro.
- **Anti-Bot Protection:** Playwright with randomized delays, human-like headers, and simulated interaction.

## Completed Tasks ✅
1.  **Multi-Site Scrapers:** FullH4rd (CSS), Compragamer (SPA/Tailwind), and Diamond Computacion (JSON-LD) fully implemented.
2.  **Cloud Migration:** Database migrated to Supabase; deployment ready for Streamlit Cloud.
3.  **Automation:** GitHub Actions workflow (`daily_update.yml`) configured for hands-free updates.
4.  **Data Modeling:** Added `group_name` and `category` to allow multi-store comparison and organization.
5.  **Advanced UI:** 
    *   Dashboard grouped by Category and Product.
    *   Price trend details showing savings/increases in $ and %.
    *   Quick filters (Todos, Subió, Bajó).
6.  **Reliability:** 
    *   Playwright auto-installation logic for cloud environments.
    *   Unit tests for price cleaning and Dólar Blue logic (`tests/test_logic.py`).
7.  **Skill System:** Created `scraper-architect` skill to standardize future expansions.

## Recommended Next Steps
1.  **Notification System:** Implement alerts (Discord/Telegram/Email) when a price drops below a specific threshold (e.g., > 3%).
2.  **Search Feature:** Implement "Product Mapping" to search by keyword across all sites and add results with one click.
3.  **Full Localization:** Translate the remaining English UI labels (Sidebar, metric names) to Spanish.
4.  **Export Feature:** Add a button to export price history to CSV or Excel for custom analysis.
5.  **Inflation Analysis:** Calculate prices in "Dólar Blue" (historical) to see if a product is actually getting cheaper in hard currency.

## Building and Running
-   **Local Run:** Double-click `RUN_MONITOR.bat`.
-   **Cloud Deployment:** Automatic via GitHub push to Streamlit Cloud.
-   **Manual Update:** GitHub Actions -> "Daily Price Update" -> Run Workflow.
