import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_pipeline import load_data_from_clickhouse

def descriptive_analysis():
    """
    Realiza un análisis descriptivo.
    """
    # 1. Cargar datos
    df = load_data_from_clickhouse(start_date='2019-01-01')
    
    # 2. Calcular métricas
    df['daily_return'] = df['close'].pct_change()
    df['abs_return'] = df['daily_return'].abs()
    df['volatility_range'] = (df['high'] - df['low']) / df['low']
    df['volume_change_ratio'] = df['volume'] / df['volume'].rolling(window=30).mean()

    # Rellenamos los NaNs iniciales usando el primer valor válido hacia atrás (back-fill)
    df.bfill(inplace=True)
    # Por si quedara algún NaN en medio, rellenamos hacia adelante (forward-fill)
    df.ffill(inplace=True)

    print("\n--- Comparativa de Métricas (Medias) ---")
    comparison = df.groupby('News')[['abs_return', 'volatility_range', 'volume_change_ratio']].mean().T
    
    # Manejo robusto en caso de que aún falte un grupo
    if 0 not in comparison.columns:
        comparison[0] = 0
    if 1 not in comparison.columns:
        comparison[1] = 0
        
    comparison.columns = ['Sin Noticia', 'Con Noticia']
    print(comparison)

    # 4. Visualización 
    sns.set(style="whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('Análisis de Impacto de Noticias', fontsize=16)

    comparison.T.plot(kind='bar', y='abs_return', ax=axes[0], legend=False, rot=0)
    axes[0].set_title('Retorno Absoluto Medio')
    axes[0].set_xlabel('Tipo de Día')

    sns.boxplot(data=df, x='News', y='volatility_range', ax=axes[1])
    axes[1].set_title('Distribución de la Volatilidad')
    axes[1].set_xticklabels(['Sin Noticia', 'Con Noticia'])
    axes[1].set_xlabel('')

    sns.boxplot(data=df, x='News', y='volume_change_ratio', ax=axes[2])
    axes[2].set_title('Distribución del Volumen Relativo')
    axes[2].set_xticklabels(['Sin Noticia', 'Con Noticia'])
    axes[2].set_xlabel('')
    axes[2].set_ylim(0, df['volume_change_ratio'].quantile(0.95))

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig('output/impact_analysis_final.png')
    print("\nGráfico 'impact_analysis_final.png' guardado.")
if __name__ == "__main__":
    descriptive_analysis()