import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from src.data_pipeline import load_data_from_clickhouse

def event_study_analysis():
    """cd
    Realiza un 'event study'. Versión final que imputa los valores NaN de los retornos
    en lugar de eliminar filas.
    """
    # 1. Cargar y unir datos (esta parte ya funciona)
    df_toyota = load_data_from_clickhouse(start_date='2019-01-01')
    print("Descargando datos del mercado (S&P 500)...")
    df_market = yf.download('^GSPC', start=df_toyota.index.min(), end=df_toyota.index.max())
    
    market_close_series = df_market['Close']
    df = df_toyota.join(market_close_series, how='inner')
    df.rename(columns={'^GSPC': 'market_close'}, inplace=True)
    
    # --- LÓGICA CORREGIDA PARA MANEJAR NaNs ---
    # 2. Calcular retornos y rellenar el único NaN con 0
    df['toyota_return'] = df['close'].pct_change().fillna(0)
    df['market_return'] = df['market_close'].pct_change().fillna(0)
    # Ya no necesitamos la línea df.dropna()
    # ---------------------------------------------
    
    # 3. El resto del código ahora encontrará los datos que necesita
    estimation_df = df[df['News'] == 0]
    if estimation_df.empty:
        print("\nError: No hay suficientes datos 'Sin Noticia' para estimar el modelo de mercado.")
        return
        
    X = estimation_df[['market_return']]
    y = estimation_df['toyota_return']
    
    model = LinearRegression()
    model.fit(X, y)
    beta = model.coef_[0]
    alpha = model.intercept_
    print(f"\n--- Modelo de Mercado Estimado ---")
    print(f"Beta (β) de Toyota: {beta:.4f}")
    print(f"Alpha (α) de Toyota: {alpha:.4f}")

    df['expected_return'] = alpha + beta * df['market_return']
    df['abnormal_return'] = df['toyota_return'] - df['expected_return']

    event_dates = df[df['News'] == 1].index
    window_size = 5
    event_window_returns = []

    for date in event_dates:
        try:
            start_index = df.index.get_loc(date) - window_size
            end_index = df.index.get_loc(date) + window_size + 1
            if start_index >= 0 and end_index <= len(df):
                event_window_returns.append(df.iloc[start_index:end_index]['abnormal_return'].values)
        except KeyError:
            print(f"Aviso: La fecha de evento {date.date()} no se encontró en el dataframe combinado (probablemente un festivo).")
            continue

    if not event_window_returns:
        print("\nError: No se pudieron crear ventanas de eventos. Revisa las fechas.")
        return

    avg_abnormal_returns = np.mean(event_window_returns, axis=0)
    cumulative_avg_abnormal_returns = np.cumsum(avg_abnormal_returns)
    
    window_days = range(-window_size, window_size + 1)
    plt.figure(figsize=(12, 7))
    plt.plot(window_days, cumulative_avg_abnormal_returns * 100, marker='o', linestyle='--')
    plt.axhline(0, color='grey', lw=1)
    plt.axvline(0, color='red', linestyle=':', label='Día del Evento (Noticia)')
    plt.title('Retorno Anormal Acumulado Medio (CAAR) alrededor del Día de la Noticia')
    plt.xlabel(f'Días Relativos al Evento (-{window_size} a +{window_size})')
    plt.ylabel('CAAR (%)')
    plt.legend()
    plt.grid(True)
    plt.savefig('output/event_study_caar.png')
    print("\nGráfico 'event_study_caar.png' guardado.")
if __name__ == "__main__":
    event_study_analysis()