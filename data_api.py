import requests
import os
from dotenv import load_dotenv
import json

load_dotenv('credenciales.env')  # Cargamos las credenciales necesarias
API_KEY = os.getenv('ALPHA_VANTAGE_API')
SYMBOL = 'TM'   # Símbolo de Toyota Motors : NYSE
DATA_FILE_PATH = 'toyota_daily_data.json' # Fichero para guardar/leer los datos

def fetch_and_save_data():
    """Realiza la llamada a la API y guarda los datos si tiene éxito."""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={SYMBOL}&outputsize=full&apikey={API_KEY}'
    
    try:
        r = requests.get(url)
        r.raise_for_status() # Lanza un error para códigos HTTP 4xx/5xx
        data = r.json()

        # Comprobar si la API devolvió un error de límite en lugar de datos
        if "Information" in data:
            print(f"Error de la API: {data['Information']}")
            return None
        
        # Si la llamada fue exitosa, guarda los datos
        with open(DATA_FILE_PATH, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Datos guardados exitosamente en {DATA_FILE_PATH}")
        return data

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición HTTP: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: La respuesta de la API no es un JSON válido.")
        return None

def get_stock_data():
    """Obtiene los datos, ya sea del fichero local o de la API."""
    if os.path.exists(DATA_FILE_PATH):
        print(f"Cargando datos desde el fichero local: {DATA_FILE_PATH}")
        with open(DATA_FILE_PATH, 'r') as f:
            return json.load(f)
    else:
        print("No se encontraron datos locales. Realizando llamada a la API...")
        return fetch_and_save_data()


if __name__ == "__main__":
    stock_data = get_stock_data()
    
    if stock_data:
        # Extraer la serie temporal del JSON
        time_series = stock_data.get("Time Series (Daily)")
        
        if time_series:
            # Imprimir solo los primeros 5 registros para comprobar los datos rápidamente
            first_5_days = list(time_series.items())[:5]
            print("\n--- Primeros 5 registros de la serie temporal ---")
            for date, values in first_5_days:
                print(f"{date}: {values}")
        else:
            print("\nLa clave 'Time Series (Daily)' no se encontró en la respuesta. Revisa el JSON completo:")
            print(stock_data)