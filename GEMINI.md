# GEMINI.md - Project Context

## Project Overview
`segundo-proyecto` is a **Multi-Site Price Monitor (Backend Focus)** application. Its goal is to track, compare, and notify price changes of specific products on pre-defined e-commerce websites (Compragamer, FullH4rd, Diamond Computacion).

**Key Features:**
- **Product Mapping & Selection:** User searches for a general term, sees results from configured sites, and manually selects specific products to track (via URL).
- **Modular Scraping:** Individual scraper modules per store to facilitate maintenance.
- **Price Comparison Engine:** Analyzes current price vs. last saved price and historical minimums.
- **Smart Analysis:** Calculates price trends (arrows) and 30-day medians to detect "Inflated Prices" vs. "Real Opportunities".
- **Local Database (SQLite):** Stores tracked products (URL, chosen name, store) and price history (timestamp, detected price).
- **Smart Notification Logic:** Alerts for price drops exceeding a configurable threshold (e.g., 2%), highlighting "OFFER" or "NEW MINIMUM." Will also track prices against "Dólar Blue" for context in Argentina.
- **Anti-Bot Protection:** Implements randomized delays, realistic headers, and simulated interaction (scroll) to avoid IP bans.
- **Failure Management:** Implements a "2-Attempt Policy" for scraping failures (5-minute delay before retry).
- **On-Demand Execution:** The process runs only when manually triggered, completing a full session (load URLs, scrape, compare, notify, close).

## Technology Stack
-   **Language:** Python 3.10+
-   **Scraping:** Playwright + BeautifulSoup4.
-   **Database:** SQLite with SQLAlchemy ORM.
-   **Web Interface (Simple):** Streamlit.
-   **Data Visualization:** Pandas + Streamlit native charts (st.line_chart).

## Completed Tasks ✅
1.  **Project Structure:** Base directory structure created (`src/`, `data/`, etc.).
2.  **Environment Setup:** Virtual environment created and dependencies installed (`requirements.txt`).
3.  **Database Implementation:** Models defined (`models.py`) and manager created (`db_manager.py`) with SQLAlchemy.
4.  **FullH4rd Scraper:** Initial implementation and subsequent update with anti-bot protection (delays, headers, scroll).
5.  **Compragamer Scraper:** Implementation of a robust scraper for SPA (Single Page Application) using Playwright + BeautifulSoup.
6.  **Dólar Blue Logic:** Implemented in `dolar_utils.py` using Bluelytics API.
7.  **Skill System:** Created and installed the `scraper-architect` skill to standardize the creation of future scrapers.
8.  **Advanced Analysis Engine:**
    *   Trend detection (green/red arrows) based on previous price.
    *   30-day median calculation to detect "Inflated Prices" (I > 1.10).
    *   "Real Opportunity" indicator (Price < Median * 0.95).
9.  **UI Redesign:** Dashboard updated with Quick Filters (All, Opportunities, Minimums, Inflated).
10. **Usability:** Created `RUN_MONITOR.bat` for one-click execution without terminal commands.

## Building and Running
-   **Build Command:** `pip install -r requirements.txt`
-   **Run Command:** Double-click `RUN_MONITOR.bat` (or `streamlit run src/main.py`)
-   **Test Command:** `.venv\Scripts\python.exe .gemini\skills\scraper-architect\scripts\test_new_scraper.py <path_to_scraper> <url>`

## Recommended Next Steps
1.  **Implement DiamondSystem Scraper:** Add support for the third target site following the `scraper-architect` standards.
2.  **Notification System:** Implement the logic to detect price drops (2% threshold) and show alerts in the UI.
3.  **Search Feature:** Implement "Product Mapping" to allow searching by keyword across sites instead of only by direct URL.
4.  **Batch Update Optimization:** Refine the background process to handle more products simultaneously if the list grows.
