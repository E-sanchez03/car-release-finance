import os
from clickhouse_driver import Client
from dotenv import load_dotenv

load_dotenv('credenciales.env')
# --- Configuración ---
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_USER = os.getenv('CH_USER')      
CLICKHOUSE_PASSWORD = os.getenv('CH_PASSWORD') 
DB_NAME = 'stocks_db'

# --- Comandos SQL ---
CREATE_DB_SQL = f"CREATE DATABASE IF NOT EXISTS {DB_NAME};"   

CREATE_TABLE_SQL = f"""
CREATE TABLE IF NOT EXISTS {DB_NAME}.stock_daily
(
    `ticker` String,
    `event_date` Date,
    `open` Float64,
    `high` Float64,
    `low` Float64,
    `close` Float64,
    `volume` UInt64
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(event_date)
ORDER BY (ticker, event_date);
"""
ADD_COLUMNS = [f"""
ALTER TABLE stocks_db.stock_daily ADD COLUMN IF NOT EXISTS News UInt8 DEFAULT 0;""",
f"""ALTER TABLE stocks_db.stock_daily ADD COLUMN IF NOT EXISTS News_Type Nullable(String) DEFAULT NULL;
"""]

def main():
    """
    Se conecta a la base de datos 'default', crea la base de datos
    del proyecto y luego crea la tabla necesaria, en pasos separados.
    """
    client = None
    try:
        print(">> Paso 1: Conectando al servidor de ClickHouse...")
        client = Client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            user=CLICKHOUSE_USER,
            password=CLICKHOUSE_PASSWORD,
            database='default' 
        )
        print("   Conexión establecida.")

        print(f">> Paso 2: Creando la base de datos '{DB_NAME}'...")
        client.execute(CREATE_DB_SQL)
        print(f"   Base de datos '{DB_NAME}' creada o ya existente.")
        # PASO 3: Ejecutar el SEGUNDO comando para crear la tabla.
        print(f">> Paso 3: Creando la tabla 'stock_daily'...")
        client.execute(CREATE_TABLE_SQL)
        print("   Tabla 'stock_daily' creada o ya existente.")
        print(f" >> Añadir columnas relacionadas con noticias ...")
        client.execute(ADD_COLUMNS[0])
        client.execute(ADD_COLUMNS[1])
        print("\n✅ ¡Inicialización de la base de datos completada exitosamente!")

    except Exception as e:
        print(f"\n❌ Error fatal durante la inicialización: {e}")
    finally:
        if client:
            client.disconnect()
            print("\n🔌 Conexión a ClickHouse cerrada.")

if __name__ == "__main__":
    main()