import os
from datetime import datetime
from clickhouse_driver import Client
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv('credenciales.env')
# --- Configuración ---
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = os.getenv('CH_USER')      
CLICKHOUSE_PASSWORD = os.getenv('CH_PASSWORD') 
DB_NAME = 'stocks_db'
NEWS_FILE_PATH = 'noticias.txt' 

def scrape_news_date(url):
    """
    Visita una URL, parsea su HTML y extrae la fecha de publicación.
    Versión actualizada para manejar múltiples formatos de fecha.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'} # Simulamos ser un navegador
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status() # Lanza un error si la descarga falla

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- LÓGICA DE BÚSQUEDA ---
        # Buscamos en orden de prioridad los selectores que hemos identificado.
        date_element = soup.select_one('p.date, time, .p-news-head__date, .news-detail-date-wrap')
        
        if date_element:
            # La etiqueta <time> suele tener un atributo 'datetime' que es más limpio
            date_str = date_element.get('datetime', date_element.text).strip()
            
            # --- LÓGICA DE PARSEO  ---
            # Intentamos parsear la fecha con varios formatos conocidos.
            for fmt in ('%Y-%m-%d', '%B %d, %Y', '%b. %d, %Y'):
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue # Si falla, prueba el siguiente formato
            
            # Si ninguno de los formatos funcionó
            print(f"   Aviso: Formato de fecha no reconocido: '{date_str}' en {url}")
            return None
        else:
            print(f"   Aviso: No se encontró un elemento de fecha en {url}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"   Error descargando la URL {url}: {e}")
        return None
    except Exception as e:
        print(f"   Error procesando la URL {url}: {e}")
        return None

def update_clickhouse_record(client, event_date, news_type):
    """
    Ejecuta un comando ALTER TABLE...UPDATE en ClickHouse para una fecha específica.
    """
    date_str_for_query = event_date.strftime('%Y-%m-%d')
    query = f"""
    ALTER TABLE {DB_NAME}.stock_daily 
    UPDATE News = 1, News_Type = '{news_type.replace("'", "''")}'
    WHERE event_date = '{date_str_for_query}'
    """
    
    try:
        # Los settings son necesarios para que la mutación se ejecute de forma síncrona
        client.execute(query, settings={'mutations_sync': 2})
        print(f"   ✅ Registro actualizado para la fecha {date_str_for_query}")
        return True
    except Exception as e:
        print(f"   ❌ Error actualizando el registro para la fecha {date_str_for_query}: {e}")
        return False

def main():
    if not os.path.exists(NEWS_FILE_PATH):
        print(f"Error: El fichero de noticias '{NEWS_FILE_PATH}' no fue encontrado.")
        return

    client = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD, database=DB_NAME)
    print("🔌 Conexión a ClickHouse establecida.")

    with open(NEWS_FILE_PATH, 'r') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line or '->' not in line:
                continue

            url, news_type = line.split(' -> ', 1)
            print(f"\n[{i+1}] Procesando URL: {url.strip()}")

            event_date = scrape_news_date(url.strip())
            
            if event_date:
                update_clickhouse_record(client, event_date, news_type.strip())
            else:
                print("   No se pudo procesar esta noticia.")

    client.disconnect()
    print("\n🏁 Proceso finalizado. Conexión a ClickHouse cerrada.")

if __name__ == "__main__":
    main()