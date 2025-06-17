import pandas as pd
from clickhouse_driver import Client
from sklearn.preprocessing import StandardScaler
import os
from dotenv import load_dotenv

def load_data_from_clickhouse(start_date='2019-01-01'):
    """Carga los datos desde 2019 en un DataFrame de pandas."""
    load_dotenv('credenciales.env')
    client = Client(
        host=os.getenv('CH_HOST', 'localhost'),
        user=os.getenv('CH_USER'),
        password=os.getenv('CH_PASSWORD'),
        database='stocks_db'
    )
    query = f"SELECT * FROM stocks_db.stock_daily WHERE event_date >= '{start_date}' ORDER BY event_date"
    data = client.execute(query, with_column_types=True)
    
    df = pd.DataFrame(data[0], columns=[col[0] for col in data[1]])
    df['event_date'] = pd.to_datetime(df['event_date'])
    df.set_index('event_date', inplace=True)
    
    print(f"Datos cargados exitosamente. {len(df)} filas desde {start_date}.")
    return df

def feature_engineering(df):
    """Crea características y el target para el modelo."""
    # 1. Crear el Target (nuestro objetivo a predecir)
    # ¿Subirá el precio mañana? (1 si sí, 0 si no)
    df['target'] = (df['close'].shift(-1) > df['close']).astype(int)
    
    # 2. Crear Características (Features)
    # Lags de precios
    for i in range(1, 6):
        df[f'close_lag_{i}'] = df['close'].shift(i)
        df[f'volume_lag_{i}'] = df['volume'].shift(i)
        
    # Medias móviles
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_30'] = df['close'].rolling(window=30).mean()
    
    # Volatilidad
    df['volatility_30'] = df['close'].rolling(window=30).std()
    
    # RSI (Relative Strength Index)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # Features de Noticias
    # El tipo de noticia es una variable categórica, la convertimos con One-Hot Encoding
    df['News_Type'].fillna('NoNews', inplace=True) # Rellenar nulos
    news_dummies = pd.get_dummies(df['News_Type'], prefix='news_type')
    df = pd.concat([df, news_dummies], axis=1)
    
    # Limpieza final
    df.drop(['ticker', 'News_Type'], axis=1, inplace=True)
    df.dropna(inplace=True) # Eliminar filas con NaNs (generados por los lags y rolling)
    
    print("Ingeniería de características completada.")
    return df

def get_prepared_data(start_date='2019-01-01', split_date='2024-01-01'):
    """Pipeline completo que carga, procesa y divide los datos."""
    df = load_data_from_clickhouse(start_date)
    df_featured = feature_engineering(df)
    
    # Separar features (X) y target (y)
    X = df_featured.drop('target', axis=1)
    y = df_featured['target']
    
    # Dividir en Train y Test cronológicamente
    X_train, X_test = X.loc[X.index < split_date], X.loc[X.index >= split_date]
    y_train, y_test = y.loc[y.index < split_date], y.loc[y.index >= split_date]
    
    # Escalar los datos
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Convertir de vuelta a DataFrame para mantener la legibilidad
    X_train_scaled = pd.DataFrame(X_train_scaled, index=X_train.index, columns=X_train.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, index=X_test.index, columns=X_test.columns)
    
    print("Datos divididos y escalados. Listos para el entrenamiento.")
    return X_train_scaled, X_test_scaled, y_train, y_test