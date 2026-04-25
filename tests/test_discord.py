import os
import sys
from dotenv import load_dotenv

# Asegurar que la raíz del proyecto esté en el path
# Al estar en 'tests/', subimos un nivel para encontrar 'src'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.logic.notifications import send_discord_alert

def test_notification():
    load_dotenv()
    webhook = os.environ.get("DISCORD_WEBHOOK_URL")
    
    if not webhook:
        print("❌ Error: No se encontró DISCORD_WEBHOOK_URL en el archivo .env")
        return

    print("🚀 Enviando notificación de prueba a Discord...")
    
    try:
        send_discord_alert(
            product_name="Producto de Prueba",
            store="Tienda Test",
            old_price=1000.00,
            new_price=850.00,
            url="https://example.com"
        )
        print("✅ ¡Mensaje enviado! Revisa tu canal de Discord.")
    except Exception as e:
        print(f"❌ Falló el envío: {e}")

if __name__ == "__main__":
    test_notification()
