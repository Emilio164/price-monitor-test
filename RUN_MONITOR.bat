@echo off
TITLE Price Monitor Runner
echo [1/2] Activando entorno virtual...
CALL .venv\Scripts\activate
echo [2/2] Iniciando Streamlit...
streamlit run src/main.py
pause
