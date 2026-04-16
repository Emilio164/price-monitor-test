import requests
import os

def send_discord_alert(product_name, store, old_price, new_price, url):
    """
    Envía una alerta con formato de 'Embed' a Discord a través de un Webhook.
    """
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("Advertencia: DISCORD_WEBHOOK_URL no configurada.")
        return

    diff = old_price - new_price
    percent = (diff / old_price) * 100

    # Color verde para la alerta
    color = 3066993 

    payload = {
        "username": "Price Monitor Bot",
        "embeds": [{
            "title": "🔥 ¡OFERTA DETECTADA! 🔥",
            "description": f"Se ha detectado una baja de precio en **{store}**.",
            "color": color,
            "fields": [
                {
                    "name": "Producto",
                    "value": product_name,
                    "inline": False
                },
                {
                    "name": "Precio Anterior",
                    "value": f"${old_price:,.2f}",
                    "inline": True
                },
                {
                    "name": "Precio Nuevo",
                    "value": f"**${new_price:,.2f}**",
                    "inline": True
                },
                {
                    "name": "Rebaja",
                    "value": f"-${diff:,.2f} (**-{percent:.1f}%**)",
                    "inline": True
                }
            ],
            "url": url,
            "footer": {
                "text": "Multi-Site Price Monitor"
            }
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"✅ Alerta de Discord enviada para {product_name}")
    except Exception as e:
        print(f"❌ Error enviando alerta a Discord: {e}")
