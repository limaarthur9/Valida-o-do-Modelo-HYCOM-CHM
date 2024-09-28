import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt

# Função para importar os dados a partir de um arquivo .csv
def importar_dados(file_path):
    df = pd.read_csv(file_path, delimiter=',', header=0)
    
    # Ajustar o formato do timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    
    # Verificar se houve erros na conversão
    if df['timestamp'].isnull().any():
        print("Algumas datas não puderam ser convertidas. Verifique o formato dos dados.")
    
    # Configurar o índice como timestamp
    df.set_index('timestamp', inplace=True)
    
    return df

# Função para identificar as frequências de amostragem
def identificar_frequencias(df):
    time_diffs = df.index.to_series().diff().dt.total_seconds().dropna()
    freq_counts = time_diffs.value_counts().sort_index()
    return freq_counts

# Função para calcular a taxa de amostragem (em Hz)
def obter_sample_rate(time_diff):
    return 1 / (time_diff / 60)  # Retorna a taxa de amostragem em Hz

# Função para aplicar o filtro Butterworth
def aplicar_filtro(df, sample_rate, order=4):
    if not isinstance(order, int) or order <= 0:
        raise ValueError("A ordem do filtro deve ser um número inteiro positivo.")

    nyquist = 0.5 * sample_rate
    cutoff_freq = 0.1 * sample_rate
    if cutoff_freq >= nyquist:
        raise ValueError(f"Frequência de corte {cutoff_freq} inválida para a taxa de amostragem {sample_rate}.")
    
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    
    df['water_l1_Filtrado'] = filtfilt(b, a, df['water_l1'])
    return df

# Função para processar os dados
def processar_dados(file_path, file_saida, order=4):
    print(f"\nProcessando dados com a ordem do filtro Butterworth: {order}")
    print(f"Arquivo de entrada: {file_path}")
    
    # Importar os dados do arquivo de entrada
    df = importar_dados(file_path)
    
    # Identificar as frequências de amostragem
    freq_counts = identificar_frequencias(df)
    print("\nFrequências de amostragem (em segundos) e contagem:")
    print(freq_counts)

    # Focar apenas nas frequências principais (1 min, 10 min, 15 min)
    frequencias_interesse = [60, 600, 900]
    
    filtered_dfs = []
    num_linhas_cortadas = 0

    for time_diff, count in freq_counts.items():
        if time_diff in frequencias_interesse:
            sample_rate = obter_sample_rate(time_diff)
            mask = df.index.to_series().diff().dt.total_seconds() == time_diff
            df_freq = df[mask]
            
            try:
                df_filtrado = aplicar_filtro(df_freq, sample_rate, order=order)
                filtered_dfs.append(df_filtrado)
                num_linhas_cortadas += len(df) - len(df_freq)

                plt.figure(figsize=(10, 6))
                plt.plot(df_freq.index, df_freq['water_l1'], label='Dados Brutos', color='blue')
                plt.plot(df_filtrado.index, df_filtrado['water_l1_Filtrado'], label='Dados Filtrados', color='red')
                plt.xlabel('Tempo')
                plt.ylabel('Nível do Mar')
                plt.title(f'Filtro Butterworth aplicado para intervalo de {time_diff} segundos')
                plt.legend()
                plt.show()
            
            except ValueError as e:
                print(f"Erro ao aplicar o filtro para a frequência {time_diff} segundos: {e}")
    
    # Concatenar todos os DataFrames filtrados
    df_final = pd.concat(filtered_dfs)
    
    # Salvar os dados filtrados
    df_final.to_csv(file_saida, index=True)
    print(f"\nDados filtrados salvos em: {file_saida}")
    
    # Informar o número de linhas cortadas
    print(f"\nNúmero de linhas cortadas após a filtragem: {num_linhas_cortadas}")

# Exemplo de uso
arquivo_entrada = 'dados_qualidade_15min_RIB.csv'
arquivo_saida = 'dados_qualidade_RIB_filtrados.csv'
ordem_filtro = 4

processar_dados(arquivo_entrada, arquivo_saida, order=ordem_filtro)
