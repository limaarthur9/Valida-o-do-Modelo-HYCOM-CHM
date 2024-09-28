import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

def transformar_dados(input_file, output_file, estacao, ajuste_fuso=0):
    # Lendo o arquivo de entrada, ignorando as linhas de cabeçalho textual
    dados = pd.read_csv(input_file, delimiter=',', skiprows=16)  # Ignora as primeiras 10 linhas de metadados
    
    # Criando uma coluna de data/hora a partir das colunas separadas
    dados['DataHora'] = pd.to_datetime(dados[['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND']])
    
    # Ajustando o fuso horário
    dados['DataHora'] = dados['DataHora'] + pd.Timedelta(hours=ajuste_fuso)

    # Convertendo o nível do mar para centímetros
    dados['water_l1'] = dados['water_l1'].round(2)  # O dado já está em centímetros

    # Selecionando as colunas necessárias
    dados_transformados = dados[['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND', 'water_l1']]

    # Salvando o resultado no arquivo de saída
    dados_transformados.to_csv(output_file, index=False)
    
    # Definindo e imprimindo o intervalo de dados
    intervalo = dados['DataHora'].diff().dropna().min()
    if intervalo == pd.Timedelta(minutes=1):
        print("A frequência de amostragem é de 1 em 1 minuto.")
    elif intervalo == pd.Timedelta(minutes=5):
        print("A frequência de amostragem é de 5 em 5 minutos.")
    elif intervalo == pd.Timedelta(minutes=10):
        print("A frequência de amostragem é de 10 em 10 minutos.")
    elif intervalo == pd.Timedelta(minutes=15):
        print("A frequência de amostragem é de 15 em 15 minutos.")
    elif intervalo == pd.Timedelta(minutes=30):
        print("A frequência de amostragem é de 30 em 30 minutos.")
    elif intervalo == pd.Timedelta(hours=1):
        print("A frequência de amostragem é de 1 em 1 hora.")
    else:
        print(f"A frequência de amostragem é irregular ou de {intervalo}.")

    # Imprimir o período de dados
    print(f"Período de dados: {dados['DataHora'].min()} a {dados['DataHora'].max()} para a estação {estacao}")
    print(f"Dados transformados e salvos em {output_file}")

    # Plotando o gráfico
    plt.figure(figsize=(10,6))
    plt.plot(dados['DataHora'], dados['water_l1'], label='Nível do Mar (cm)')
    
    # Formatando as datas no gráfico
    date_form = DateFormatter("%d-%m-%y")
    plt.gca().xaxis.set_major_formatter(date_form)

    # Adicionando título e rótulos
    plt.title(f"Dados obtidos na estação {estacao}")
    plt.xlabel("Data")
    plt.ylabel("Nível do Mar (cm)")
    
    # Habilitando zoom e interatividade
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    # Exibir o gráfico
    plt.show()

# Exemplo de uso
input_file = 'SIMCOSTA_Ribamar_LEVEL_2024-01-01_2024-09-22.csv'  # Arquivo com formato de CSV
output_file = 'dados_pre_RIB.csv'
estacao = 'de Ribamar - MA'
transformar_dados(input_file, output_file, estacao, ajuste_fuso=2)
