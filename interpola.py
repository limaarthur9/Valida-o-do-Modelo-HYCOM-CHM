import pandas as pd
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt

# Função para ler dados modelados e observados
def read_data(file_path):
    """Lê os dados de um arquivo CSV e retorna um DataFrame."""
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

# Função para criar nova série com os timestamps observados
def create_new_series_with_timestamps(df_observed):
    """Cria uma nova série apenas com os timestamps dos dados observados."""
    df_new_series = pd.DataFrame()
    df_new_series['timestamp'] = df_observed['timestamp']
    df_new_series['Nivel_do_Mar_Interpolado'] = None
    return df_new_series

# Função para interpolar os valores de nível modelado com base nos timestamps observados
def interpolate_model_levels(df_new_series, df_model):
    """Realiza a interpolação Cubic Spline dos níveis de mar modelados para os timestamps observados."""
    # Convertendo os timestamps para números (em segundos) para a interpolação
    time_numeric_model = (df_model['timestamp'] - df_model['timestamp'].min()).dt.total_seconds()
    time_numeric_new_series = (df_new_series['timestamp'] - df_model['timestamp'].min()).dt.total_seconds()
    
    # Usando Cubic Spline para interpolar os níveis de mar modelados
    cs = CubicSpline(time_numeric_model, df_model['Nivel_do_Mar'])
    
    # Preenchendo os valores de nível na nova série
    df_new_series['Nivel_do_Mar_Interpolado'] = cs(time_numeric_new_series)
    
    return df_new_series

# Função para plotar os dados observados, modelados e interpolados com pontos pequenos
def plot_data(df_observed, df_model, df_new_series, station_name):
    """Plota todas as séries temporais juntas como gráfico de dispersão com pontos pequenos."""
    plt.figure(figsize=(14, 7))
    
    # Plotar dados observados como pontos pequenos
    plt.scatter(df_observed['timestamp'], df_observed['Nivel_do_Mar'], label='Dados Observados', color='blue', s=1, alpha=0.7)
    
    # Plotar dados modelados como pontos pequenos
    plt.scatter(df_model['timestamp'], df_model['Nivel_do_Mar'], label='Dados Modelados HYCOM', color='orange', s=1, alpha=0.7)
    
    # Plotar dados interpolados como pontos pequenos
    plt.scatter(df_new_series['timestamp'], df_new_series['Nivel_do_Mar_Interpolado'], label='Dados Interpolados', color='green', s=1, alpha=0.7)
    
    plt.xlabel('Data')
    plt.ylabel('Nível do Mar (cm)')
    plt.title(f'Comparação de Dados Observados e Modelados (HYCOM) - {station_name}')
    plt.legend()
    plt.grid(True)
    plt.show()

# Carregar os dados OBSERVADOS X MODELADOS
df_observed = read_data('dados_qualidade_RGD_filtrados.csv')  # Substitua pelo caminho correto dos dados observados
df_model = read_data('hycom_RGD.csv')  # Substitua pelo caminho correto dos dados modelados (HYCOM)

# Passo 2: Criar a nova série com timestamps observados
df_new_series = create_new_series_with_timestamps(df_observed)

# Passo 4: Interpolar os dados modelados com base nos timestamps observados
df_new_series = interpolate_model_levels(df_new_series, df_model)

# Mostrar as primeiras linhas da nova série após interpolação
print("\nNova Série (após interpolação):")
print(df_new_series.head())

# Passo 6: Plotar os dados observados, modelados e interpolados com pontos pequenos
plot_data(df_observed, df_model, df_new_series, "Rio Grande - RS")

# Passo 5: Salvar a nova série interpolada em um arquivo CSV
df_new_series.to_csv('nova_serie_interpolada_RGD.csv', index=False)
