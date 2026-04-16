import requests

def get_dolar_blue():
    """
    Fetches the current Dólar Blue price from a public API.
    Returns a dictionary with 'buy', 'sell' and 'avg' values.
    """
    try:
        # Using Bluelytics API as it's stable and public
        response = requests.get("https://api.bluelytics.com.ar/v2/latest", timeout=10)
        response.raise_for_status()
        data = response.json()
        blue = data.get('blue', {})
        return {
            'buy': blue.get('value_buy'),
            'sell': blue.get('value_sell'),
            'avg': blue.get('value_avg')
        }
    except Exception as e:
        print(f"Error fetching Dólar Blue: {e}")
        return None

if __name__ == "__main__":
    # Quick test
    dolar = get_dolar_blue()
    print(f"Dólar Blue: {dolar}")
