import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.widgets import Slider

# Função para ler o arquivo CSV
def read_csv(file_path):
    try:
        print("1. Lendo o arquivo CSV...")
        dados_mare = pd.read_csv(file_path, delimiter=',')  # Ler o arquivo com o delimitador correto
        print("Arquivo CSV lido com sucesso.")

        # Verificar se a coluna 'DataHora' está presente
        if 'DataHora' not in dados_mare.columns:
            print("Erro: A coluna 'DataHora' não foi encontrada no arquivo CSV.")
            return pd.DataFrame()

        # Utilizando a coluna 'DataHora' já existente
        dados_mare['timestamp'] = pd.to_datetime(dados_mare['DataHora'])
        print("Coluna de timestamp criada com sucesso.")
        
        return dados_mare[['timestamp', 'water_l1']]
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        
        return pd.DataFrame()

# Função para calcular parâmetros estatísticos
def calculate_statistics(data):
    print("Calculando estatísticas básicas...")
    std_dev = data['water_l1'].std()
    max_value = data['water_l1'].max()
    min_value = data['water_l1'].min()
    print(f"Desvio Padrão: {std_dev} cm, Valor Máximo: {max_value} cm, Valor Mínimo: {min_value} cm")
    return std_dev, max_value, min_value

# Função para adicionar funcionalidade de zoom e salvar gráfico, com cálculo dos limites do boxplot
def plot(data, title, plot_type, xlabel='Timestamp', ylabel='Nível do mar (cm)', station=None, save_name=None):
    print(f"Plotando gráfico com zoom: {title}...")

    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Escolher o tipo de gráfico
    if plot_type == 'scatter':
        ax.scatter(data['timestamp'], data['water_l1'], s=2)
    elif plot_type == 'line':
        ax.plot(data['timestamp'], data['water_l1'], linestyle='-', marker='o', markersize=2)
    elif plot_type == 'boxplot':
        # Gerar boxplot e calcular os limites inferior e superior
        boxplot = ax.boxplot(data['water_l1'].dropna(), vert=True, patch_artist=True)
        lower_whisker = boxplot['whiskers'][0].get_ydata()[1]
        upper_whisker = boxplot['whiskers'][1].get_ydata()[1]
        
        print(f"Limite Inferior do Boxplot: {lower_whisker:.2f} cm")
        print(f"Limite Superior do Boxplot: {upper_whisker:.2f} cm")
    
    # Título atualizado com o nome da estação
    ax.set_title(f"{title} - Estação {station}" if station else title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Formatar as datas no formato 'dd-mm-aa'
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%y'))  # Formato desejado dd-mm-aa
    plt.xticks(rotation=45)
    ax.grid(True)
    
    # Funcionalidade de Zoom
    ax_zoom = plt.axes([0.25, 0.01, 0.65, 0.03])
    zoom_slider = Slider(ax_zoom, 'Zoom', 0.1, 1.0, valinit=1.0)

    def update_zoom(val):
        ax.set_xlim([data['timestamp'].min(), data['timestamp'].max()])
        ax.set_ylim([data['water_l1'].min() * val, data['water_l1'].max() * val])
        fig.canvas.draw_idle()

    zoom_slider.on_changed(update_zoom)
    
    plt.tight_layout()
    
    # Salvar o gráfico, se solicitado
    if save_name:
        plt.savefig(f"{save_name}.png", bbox_inches='tight')
        print(f"Figura salva como {save_name}.png")
    
    plt.show()

    # Se for um boxplot, retornar os limites calculados
    if plot_type == 'boxplot':
        return lower_whisker, upper_whisker

# Teste de controle de qualidade - Syntax Test
def syntax_test(data, min_chars, max_chars):
    print("Aplicando Syntax Test...")
    data['combined'] = data['timestamp'].astype(str) + data['water_l1'].astype(str)
    data['message_length'] = data['combined'].apply(len)
    data['valid_syntax'] = data['message_length'].between(min_chars, max_chars)
    invalid_data = data[~data['valid_syntax']]
    print(f"Linhas cortadas pelo Teste de Sintaxe: {len(invalid_data)}")
    return data

# Teste de controle de qualidade - Gross Range Test
def gross_range_test(data, lower_whisker, upper_whisker):
    print(f"Aplicando Gross Range Test: limites [{lower_whisker}, {upper_whisker}] cm")
    valid_range = data['water_l1'].between(lower_whisker, upper_whisker)
    data['valid_range'] = valid_range
    total_invalid = (~valid_range).sum()
    print(f"Total de dados cortados no Gross Range Test: {total_invalid}")
    return data

# Teste de controle de qualidade - Spike Test
def spike_test(data, std_dev, spike_threshold):
    print(f"Aplicando Spike Test: limiar de picos = {spike_threshold} * desvio padrão")
    spk_ref = (data['water_l1'].shift(2) + data['water_l1'].shift(0)) / 2
    spike_val = abs(data['water_l1'] - spk_ref)
    data['spike'] = spike_val > std_dev * spike_threshold
    total_spikes = data['spike'].sum()
    print(f"Total de dados cortados no Spike Test: {total_spikes}")
    return data

# Teste de controle de qualidade - Flat Line Test
def flat_line_test(data, rep_count, eps):
    print(f"Aplicando Flat Line Test: limite = {eps} cm com {rep_count} repetições")
    flat_line = (data['water_l1'].diff().abs() < eps).rolling(window=rep_count).sum() == rep_count
    data['flat_line'] = flat_line
    total_flat_lines = flat_line.sum()
    print(f"Total de dados cortados no Flat Line Test: {total_flat_lines}")
    return data

# Teste de controle de qualidade - Rate of Change Test
def rate_of_change_test(data, std_dev, n_dev, tst_tim):
    print(f"Aplicando Rate of Change Test: desvio padrão * {n_dev}")
    rolling_std = data['water_l1'].rolling(tst_tim).std()
    data['rate_of_change'] = abs(data['water_l1'].diff()) > rolling_std * n_dev
    total_rate_of_change = data['rate_of_change'].sum()
    print(f"Total de dados cortados no Rate of Change Test: {total_rate_of_change}")
    return data


# Função principal para aplicar os testes QUARTOD
def apply_quartod_tests(input_file, output_file, station):
    # Ler o arquivo CSV
    data = read_csv(input_file)
    
    # Verificação: garantir que os dados foram lidos corretamente
    if data.empty:
        print("Erro: Nenhum dado foi lido do arquivo CSV.")
        return

    total_dados_antes = len(data)
    print(f"Total de dados antes dos testes: {total_dados_antes}")

    # Estatísticas básicas antes dos testes
    std_dev, max_value, min_value = calculate_statistics(data)

    # Gráficos de dados brutos
    plot(data, 'Gráfico de Dispersão - Dados Brutos', 'scatter', station=station, save_name=f'{station}_scatter_brutos')
    plot(data, 'Gráfico de Linha - Dados Brutos', 'line', station=station, save_name=f'{station}_linha_brutos')
    
    # Capturar os limites inferior e superior do boxplot dos dados brutos
    lower_whisker, upper_whisker = plot(data, 'Boxplot - Dados Brutos', 'boxplot', station=station, save_name=f'{station}_boxplot_brutos')

    # Parâmetros do teste QUARTOD, agora com os limites capturados do boxplot
    params = {
        'min_chars': 16,          # Syntax Test (mínimo de caracteres)
        'max_chars': 27,         # Syntax Test (máximo de caracteres)
        'user_min': lower_whisker,    # Gross Range Test (valor mínimo em cm)
        'user_max': upper_whisker,    # Gross Range Test (valor máximo em cm)
        'spike_threshold': 3,     # Spike Test (limiar em múltiplos do desvio padrão)
        'n_dev': 3,               # Rate of Change Test (número de desvios padrão)
        'rep_cnt_fail': 5,        # Flat Line Test (repetições para falha)
        'eps': 0.01,              # Flat Line Test (variação mínima em cm)
        'tst_tim': 375           # Tempo de teste em número de observações
    }

    # Aplicar testes QUARTOD
    print("Aplicando testes QUARTOD...")

    # Etapa 1 - Teste de Sintaxe
    data = syntax_test(data, params['min_chars'], params['max_chars'])

    # Etapa 2 - Gross Range Test (agora com os limites do boxplot)
    data = gross_range_test(data, params['user_min'], params['user_max'])

    # Etapa 3 - Spike Test
    data = spike_test(data, std_dev, params['spike_threshold'])

    # Etapa 4 - Rate of Change Test
    data = rate_of_change_test(data, std_dev, params['n_dev'], params['tst_tim'])

    # Etapa 5 - Flat Line Test
    data = flat_line_test(data, params['rep_cnt_fail'], params['eps'])

    # Filtrar dados aprovados
    valid_data = data[
        data['valid_syntax'] &
        data['valid_range'] &
        ~data['spike'] &
        ~data['rate_of_change'] &
        ~data['flat_line']
    ]
    
    print(f"Total de dados após os testes: {len(valid_data)}")

    # Salvar dados aprovados
    valid_data[['timestamp', 'water_l1']].to_csv(output_file, index=False)
    print(f"Dados aprovados salvos em {output_file}")

    # Gráficos de dados aprovados
    plot(valid_data, 'Gráfico de Dispersão - Dados Aprovados', 'scatter', station=station, save_name=f'{station}_scatter_aprovados')
    plot(valid_data, 'Gráfico de Linha - Dados Aprovados', 'line', station=station, save_name=f'{station}_linha_aprovados')
    plot(valid_data, 'Boxplot - Dados Aprovados', 'boxplot', station=station, save_name=f'{station}_boxplot_aprovados')

# Função para rodar o script
def run_analysis():
    # Arquivos de entrada e saída, e nome da estação
    input_file = 'dados_pre_RIB.csv'  # Caminho do arquivo de entrada
    output_file = 'dados_qualidade_RIB.csv'  # Caminho do arquivo de saída
    station = 'Ribamar - MA'  # Nome da estação para os títulos e arquivos
    
    # Chamar a função principal
    apply_quartod_tests(input_file, output_file, station)

# Executar a análise
run_analysis()
