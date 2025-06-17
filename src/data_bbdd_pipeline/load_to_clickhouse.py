import json
import os
from datetime import datetime
from dotenv import load_dotenv
from clickhouse_driver import Client

load_dotenv('credenciales.env')
# --- Configuración ---
DATA_FILE_PATH = 'toyota_daily_data.json'
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = os.getenv('CH_USER')      
CLICKHOUSE_PASSWORD = os.getenv('CH_PASSWORD')
DB_NAME = 'stocks_db'
TICKER_SYMBOL = 'TM' # Símbolo bursátil para Toyota Motor (NYSE)

def transform_alpha_vantage_json(json_data, ticker):
    """
    Transforma el JSON de 'TIME_SERIES_DAILY'.
    """
    time_series_key = "Time Series (Daily)"
    if time_series_key not in json_data:
        print(f"Error: La clave '{time_series_key}' no se encuentra en el JSON.")
        return []

    daily_data = json_data[time_series_key]
    rows_to_insert = []

    for date_str, values in daily_data.items():
        try:
            row = [
                ticker,
                datetime.strptime(date_str, '%Y-%m-%d').date(),
                float(values['1. open']),
                float(values['2. high']),
                float(values['3. low']),
                float(values['4. close']),
                int(values['5. volume']) 
            ]
            rows_to_insert.append(row)
        except (ValueError, KeyError) as e:
            print(f"Aviso: Saltando fila para la fecha {date_str} debido a un error de formato o clave faltante: {e}")
            continue
    return rows_to_insert

def main():
    client = None
    try:
        print(">> Conectando a la base de datos de ClickHouse...")
        client = Client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database=DB_NAME
        )
        print("   Conexión establecida exitosamente.")

    except Exception as e:
        print(f"Error fatal: No se pudo conectar a ClickHouse. Error: {e}")
        return

    if not os.path.exists(DATA_FILE_PATH):
        print(f"Error fatal: El fichero de datos '{DATA_FILE_PATH}' no fue encontrado.")
        client.disconnect()
        return
    with open(DATA_FILE_PATH, 'r') as f:
        stock_json = json.load(f)

    print(">> Transformando datos del JSON...")
    data_for_insertion = transform_alpha_vantage_json(stock_json, TICKER_SYMBOL)
    if not data_for_insertion:
        print("No se generaron datos para la inserción. Abortando.")
        client.disconnect()
        return
    print(f"   Datos transformados. {len(data_for_insertion)} filas listas para ser insertadas.")

    # --- LÓGICA DE INSERCIÓN EN LOTES ---
    try:
        print(">> Iniciando inserción de datos en ClickHouse por lotes...")
        
        chunk_size = 2000  # Insertaremos las filas en grupos de 2000
        total_rows = len(data_for_insertion)
        
        for i in range(0, total_rows, chunk_size):
            chunk = data_for_insertion[i:i + chunk_size]
            print(f"   Insertando lote de {len(chunk)} filas (desde la fila {i+1})...")
            
            client.execute(
                'INSERT INTO stock_daily VALUES',
                chunk
            )
        
        print("\n✅ ¡Inserción completada exitosamente!")

    except Exception as e:
        print(f"❌ Error durante la inserción de datos: {e}")
    finally:
        if client:
            client.disconnect()
            print("\n🔌 Conexión a ClickHouse cerrada.")

if __name__ == "__main__":
    main()