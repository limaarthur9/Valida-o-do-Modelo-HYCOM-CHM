#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 18:37:59 2024

@author: arthurlimaverde
"""

import pandas as pd
import numpy as np

def classificar_amostragem(interval):
    # Define faixas para amostragem
    if np.isclose(interval.total_seconds(), 60, atol=30):  # 1 min
        return '1_min'
    elif np.isclose(interval.total_seconds(), 300, atol=30):  # 5 min
        return '5_min'
    elif np.isclose(interval.total_seconds(), 600, atol=30):  # 10 min
        return '10_min'
    elif np.isclose(interval.total_seconds(), 900, atol=30):  # 15 min
        return '15_min'
    else:
        return 'outro'

def processar_amostragem(input_file):
    # Lendo o arquivo CSV
    dados = pd.read_csv(input_file)
    
    # Criando a coluna 'DataHora' a partir das colunas separadas
    dados['DataHora'] = pd.to_datetime(dados[['YEAR', 'MONTH', 'DAY', 'HOUR', 'MINUTE', 'SECOND']])
    
    # Calculando a diferença de tempo entre as amostras
    dados['diff'] = dados['DataHora'].diff()
    
    # Classificando a amostragem
    dados['amostragem'] = dados['diff'].apply(classificar_amostragem)
    
    # Criar um dicionário para armazenar as diferentes séries de amostragem
    series_amostragem = {}
    
    # Agrupar os dados com base na classificação de amostragem
    for amostragem, grupo in dados.groupby('amostragem'):
        series_amostragem[amostragem] = grupo.drop(columns=['diff', 'amostragem'])
        print(f"Série com amostragem de {amostragem.replace('_', ' ')}")
        print(f"Período de dados: {grupo['DataHora'].min()} a {grupo['DataHora'].max()}")
        print(f"Quantidade de dados: {len(grupo)}\n")
        
        # Salvando cada série de dados em um arquivo CSV separado
        output_file = f'dados_{amostragem}.csv'
        series_amostragem[amostragem].to_csv(output_file, index=False)
        print(f"Série salva em: {output_file}\n")

# Exemplo de uso
input_file = 'dados_pre_RIB.csv'  # Substitua pelo caminho do seu arquivo .csv
processar_amostragem(input_file)
