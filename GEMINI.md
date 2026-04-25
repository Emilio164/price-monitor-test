# GEMINI.md - Project Context

## Project Overview
`segundo-proyecto` is a **Multi-Site Price Monitor (Cloud-Native)** application. Its goal is to track, compare, and notify price changes across Compragamer, FullH4rd, and Diamond Computacion.

**Key Features:**
- **Hybrid Architecture:** Uses Supabase (PostgreSQL) in the cloud and SQLite locally (optional).
- **Inflation Analysis:** Historical tracking of "Dólar Blue" to detect real vs. nominal discounts. Includes an ARS/USD toggle in the UI.
- **Instant Performance:** Implementation of `st.cache_data` for fluid navigation and filtering.
- **Intelligent Matching:** Universal engine that groups identical products by technical specs (Hz, DDR, GB, TB, Watts) and brands.
- **Advanced Stealth:** 
    - Anti-Playwright injection (hides `navigator.webdriver`).
    - Smart Cloud Detection: Automatic headless mode in Streamlit Cloud/GitHub and headed mode in Local.
    - Randomized User-Agents (Chrome/Windows only) and Viewports.
    - Human-like interaction (mouse movements, variable scrolling).
- **Robustness:** 
    - Automatic retry logic (max 2) with backoff.
    - Intelligent block detection (Cloudflare, Ray ID, Captchas).
    - Success summary in logs (e.g., "15/15 products updated").
- **Manual Control:** "Unlink" button (🔓) to fix matching errors and move products to their own groups.
- **Visual Savings:** Shows exact discount in currency ($) and percentage (%) vs last record.

## Completed Tasks ✅
1.  **Multi-Site Scrapers:** FullH4rd, Compragamer, and Diamond Computacion fully implemented and cloud-ready.
2.  **Cloud Sync:** Database fully migrated to Supabase with hybrid connection logic.
3.  **Universal Matching Engine:** Enhanced `matcher.py` with unit conflict detection and critical variants (RGB, PRO, FE).
4.  **Inflation Analysis:** Integration of Dólar API and historical currency toggle (ARS/USD) in Dashboard.
5.  **Performance:** Implementation of caching logic to make filters instantaneous.
6.  **Security & Stealth:** 
    - Full localization to Spanish.
    - Advanced evasion of anti-bot systems (Cloudflare bypass).
    - Verified consistency between User-Agent and Browser Engine.
7.  **Notification System:** Discord integration active for price drops (> 2%).
8.  **Professional UI:** Dashboard grouped by Category, interactive charts, and quick currency switching.
9.  **Data Integrity:** Manual unlinking tool (🔓) and robust sorting logic (None-safe).

## Recommended Next Steps
1.  **Search Feature:** Implement "Product Search" to find products by keyword across all sites and add them with one click.
2.  **Export Feature:** Add a button to export price history to CSV or Excel.
3.  **Interactive Charts:** Replace native charts with Plotly for detailed tooltips and zoom.
4.  **Price Targets:** Allow setting a specific price goal to trigger special alerts.

## Building and Running
-   **Local Run:** Double-click `RUN_MONITOR.bat` (Loads `.env` with `DATABASE_URL`).
-   **Cloud Deployment:** Automatic via GitHub push to Streamlit Cloud.
-   **Manual Update:** GitHub Actions -> "Daily Price Update" -> Run Workflow.
-   **Test Notification:** `python tests/test_discord.py`.
