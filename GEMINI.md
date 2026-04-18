# GEMINI.md - Project Context

## Project Overview
`segundo-proyecto` is a **Multi-Site Price Monitor (Cloud-Native)** application. Its goal is to track, compare, and notify price changes across Compragamer, FullH4rd, and Diamond Computacion.

**Key Features:**
- **Hybrid Architecture:** Uses Supabase (PostgreSQL) in the cloud and SQLite locally.
- **Automated Scraping:** GitHub Actions updates prices daily with a randomized start (08:00 - 08:30 AM ART) to optimize runner minutes.
- **Intelligent Grouping:** Compares the same product across different stores in a unified view.
- **Smart Analysis:** Detects "Inflated Prices" vs "Real Opportunities" using 30-day medians and trend arrows.
- **Ahorro Visual:** Muestra la rebaja exacta en monto fijo ($) y porcentaje (%) frente al último registro.
- **Anti-Bot Protection:** Playwright with randomized delays, User-Agent rotation, shuffled product order, and human-like interaction.
- **Robustness:** Automatic retry logic (max 2), block detection (403/429, captchas), and debug HTML logging.

## Completed Tasks ✅
1.  **Multi-Site Scrapers:** FullH4rd (CSS), Compragamer (SPA/Tailwind), and Diamond Computacion (JSON-LD) fully implemented.
2.  **Cloud Migration:** Database migrated to Supabase; deployment ready for Streamlit Cloud.
3.  **Automation:** GitHub Actions workflow (`daily_update.yml`) configured for hands-free updates.
4.  **Data Modeling:** Added `group_name` and `category` to allow multi-store comparison and organization.
5.  **Advanced UI:** 
    *   Dashboard grouped by Category and Product.
    *   Price trend details showing savings/increases in $ and %.
    *   Quick filters (Todos, Subió, Bajó) with active state highlighting.
6.  **Reliability:** 
    *   Playwright auto-installation logic for cloud environments.
    *   Block detection and automatic debug logging (HTML captures).
    *   Scalable architecture using mapping dictionaries for easy store expansion.
7.  **Full Localization:** UI completely translated to Spanish (Panel de Control, Navegación, métricas, etc.).
8.  **Skill System:** Created `scraper-architect` skill to standardize future expansions.

## Recommended Next Steps
1.  **Notification System:** Implement alerts (Discord/Telegram/Email) when a price drops below a specific threshold (e.g., > 3%). Current Discord integration is basic (2% drop).
2.  **Search Feature:** Implement "Product Mapping" to search by keyword across all sites and add results with one click.
3.  **Export Feature:** Add a button to export price history to CSV or Excel for custom analysis.
4.  **Inflation Analysis:** Calculate prices in "Dólar Blue" (historical) to see if a product is actually getting cheaper in hard currency.

## Building and Running
-   **Local Run:** Double-click `RUN_MONITOR.bat`.
-   **Cloud Deployment:** Automatic via GitHub push to Streamlit Cloud.
-   **Manual Update:** GitHub Actions -> "Daily Price Update" -> Run Workflow.
