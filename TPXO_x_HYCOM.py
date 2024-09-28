import pandas as pd
from scipy.interpolate import CubicSpline
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import pearsonr

# Definição das cores e estilos para cada tipo de dado
COLOR_OBSERVED = 'blue'
COLOR_MODELED = 'orange'
COLOR_ADJUSTED_OBSERVED = 'darkblue'
LINE_WIDTH = 1  # Largura das linhas ajustada
ALPHA = 0.6  # Transparência ajustada

def read_model_data(file_path):
    """Lê os dados Modelados IHO do arquivo e retorna um DataFrame com datetime e Nivel_do_Mar."""
    df_model = pd.read_csv(file_path)
    df_model['timestamp'] = pd.to_datetime(df_model['timestamp'])
    return df_model

def read_observed_data(file_path):
    """Lê os dados Modelados do arquivo CSV."""
    df_observed = pd.read_csv(file_path)
    df_observed['timestamp'] = pd.to_datetime(df_observed['timestamp'])
    return df_observed

def plot_data(df_observed, df_model, station_name):
    """Plota todas as séries temporais juntas para comparação com destaques."""
    plt.figure(figsize=(14, 7))
    
    plt.plot(df_model['timestamp'], df_model['Nivel_do_Mar'], label='Dados Modelados TPXO (Referência)', color=COLOR_MODELED, linestyle='-', linewidth=2, alpha=0.7)
    plt.plot(df_observed['timestamp'], df_observed['Nivel_do_Mar'], label='Dados Modelados HYCOM (A Verificar)', color=COLOR_OBSERVED, linestyle='-', linewidth=1.5, alpha=0.7)
    
    plt.xlabel('Data')
    plt.ylabel('Nível do Mar (cm)')
    plt.title(f'Comparação entre Dados Modelados TPXO e Modelados HYCOM - {station_name}')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_adjusted_data(df_observed, df_model, station_name):
    """Plota as diferenças entre os dados Modelados e Modelados TPXO subtraídos por suas médias."""
    media_model = df_model['Nivel_do_Mar'].mean()  # A referência
    media_observada = df_observed['Nivel_do_Mar'].mean()

    df_model['Desvio_Modelado'] = df_model['Nivel_do_Mar'] - media_model
    df_observed['Desvio_Observado'] = df_observed['Nivel_do_Mar'] - media_observada
    
    plt.figure(figsize=(14, 7))
    plt.plot(df_model['timestamp'], df_model['Desvio_Modelado'], label='Desvio dos Dados Modelados TPXO (Referência)', color=COLOR_MODELED, linestyle='-', linewidth=2, alpha=0.7)
    plt.plot(df_observed['timestamp'], df_observed['Desvio_Observado'], label='Desvio dos Dados Modelados HYCOM (A Verificar)', color=COLOR_ADJUSTED_OBSERVED, linestyle='-', linewidth=2, alpha=0.7)
    
    plt.xlabel('Data')
    plt.ylabel('Desvio do Nível do Mar (cm)')
    plt.title(f'Comparação de Desvios Ajustados - {station_name}')
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_statistics_barron(modeled, observed, description="Original"):
    """Calcula e exibe estatísticas entre dados Modelados TPXO e Modelados HYCOM usando o skill de Barron."""
    
    # Cálculo das métricas
    rmse = np.sqrt(mean_squared_error(modeled, observed))
    mae = mean_absolute_error(modeled, observed)
    r, _ = pearsonr(modeled, observed)
    d = 1 - (np.sum((modeled - observed) ** 2) / np.sum((np.abs(observed - np.mean(modeled)) + np.abs(modeled - np.mean(modeled))) ** 2))
    
    # Cálculo do "range médio do dado" conforme Barron et al. (2004)
    range_medio_barron = (2 / len(modeled)) * np.sum(np.abs(modeled - np.mean(modeled)))
    
    # Skill Score de Barron
    skill_barron = 1 - (rmse / range_medio_barron)
    
    # Exibição dos resultados
    print(f"\nEstatísticas {description} - Skill de Barron:")
    print(f"RMSE: {rmse:.4f}")
    print(f"MAE: {mae:.4f}")
    print(f"Coeficiente de Correlação de Pearson (r): {r:.4f}")
    print(f"Índice de Willmott (d): {d:.4f}")
    print(f"Skill de Barron: {skill_barron:.4f}")
    
    return skill_barron

# Função principal adaptada para calcular o skill de Barron
def main():
    model_file_path = 'tpxo_RIB.csv'     # Nome do arquivo com dados de previsão TPXO
    observed_file_path = 'nova_serie_interpolada_RIB.csv'   # Nome do arquivo com dados Modelados do HYCOM
    station_name = 'Ribamar - MA'         # Nome da estação por extenso
    
    df_model = read_model_data(model_file_path)
    df_observed = read_observed_data(observed_file_path)
    
    # Plotar dados originais
    plot_data(df_observed, df_model, station_name)
    
    # Cálculo e plotagem das séries ajustadas
    plot_adjusted_data(df_observed, df_model, station_name)
    
    # Remover NaNs dos dados Modelados e modelados
    df_observed = df_observed.dropna(subset=['Nivel_do_Mar'])
    df_model = df_model.dropna(subset=['Nivel_do_Mar'])
    
    # Garantir que estamos comparando as séries corretamente alinhadas
    modeled = df_model['Nivel_do_Mar'].values  # Agora, os dados do TPXO são a referência
    observed = df_observed['Nivel_do_Mar'].values

    # Calcular estatísticas com Skill de Barron
    calculate_statistics_barron(modeled, observed, "Original")

    # Calcular estatísticas para dados ajustados
    desvio_modelado = modeled - np.mean(modeled)
    desvio_observado = observed - np.mean(observed)
    calculate_statistics_barron(desvio_modelado, desvio_observado, "Ajustados")




if __name__ == "__main__":
    main()
