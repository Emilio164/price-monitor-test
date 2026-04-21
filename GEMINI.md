# GEMINI.md - Project Context

## Project Overview
`segundo-proyecto` is a **Multi-Site Price Monitor (Cloud-Native)** application. Its goal is to track, compare, and notify price changes across Compragamer, FullH4rd, and Diamond Computacion.

**Key Features:**
- **Hybrid Architecture:** Uses Supabase (PostgreSQL) in the cloud and SQLite locally (optional).
- **Automated Scraping:** GitHub Actions updates prices daily with a randomized start (08:00 - 08:30 AM ART) to optimize runner minutes.
- **Intelligent Matching:** Universal engine that groups identical products across stores by analyzing technical specs (Hz, TB, GB, Watts) and brands, avoiding manual grouping.
- **Advanced Stealth:** 
    - Anti-Playwright injection (hides `navigator.webdriver`).
    - Randomized User-Agents (Chrome/Windows) and Viewports.
    - Human-like interaction (mouse movements, variable scrolling).
- **Robustness:** 
    - Automatic retry logic (max 2).
    - Intelligent block detection (403, 429, Cloudflare Ray ID, real Captchas).
    - Debug HTML logging with GitHub Artifacts integration.
- **Smart Analysis:** Detects "Inflated Prices" vs "Real Opportunities" using 30-day medians and trend arrows.
- **Visual Savings:** Shows exact discount in currency ($) and percentage (%) vs last record.

## Completed Tasks ✅
1.  **Multi-Site Scrapers:** FullH4rd, Compragamer, and Diamond Computacion fully implemented and scalable via Mapping Dictionary.
2.  **Cloud Sync:** Database fully migrated to Supabase with hybrid connection logic (.env local / Secrets remote).
3.  **Universal Matching Engine:** Implementation of `matcher.py` for technical spec extraction and automatic product grouping.
4.  **Security & Stealth:** 
    - Full localization to Spanish.
    - Professional `.gitignore` for secrets and logs.
    - Advanced evasion of anti-bot systems (Cloudflare bypass).
5.  **Notification System:** Discord integration active for price drops (> 2%).
6.  **Advanced UI:** 
    *   Dashboard grouped by Category and Product.
    *   Auto-suggestion of Groups/Categories when adding new URLs.
    *   Quick filters (Todos, Subió, Bajó) with active state highlighting.
7.  **Diagnostic Tools:** Automatic HTML capture on errors and GitHub Artifacts configuration.

## Recommended Next Steps
1.  **Performance Optimization:** Implement `st.cache_data` in Streamlit to make filters instantaneous for large product lists.
2.  **Search Feature:** Implement "Product Search" to find products by keyword across all sites and add them with one click.
3.  **Export Feature:** Add a button to export price history to CSV or Excel.
4.  **Inflation Analysis:** Calculate prices in "Dólar Blue" (historical) to detect real vs. nominal discounts.

## Building and Running
-   **Local Run:** Double-click `RUN_MONITOR.bat` (Ensure `.env` with `DATABASE_URL` exists).
-   **Cloud Deployment:** Automatic via GitHub push to Streamlit Cloud.
-   **Manual Update:** GitHub Actions -> "Daily Price Update" -> Run Workflow.
-   **Test Notification:** `python test_discord.py`.
