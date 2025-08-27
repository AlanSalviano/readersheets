import pandas as pd

def calcular_pagamento_individual(row, weekly_data):
    """Calcula o pagamento individual de cada atendimento"""
    tech_week_data = weekly_data[
        (weekly_data['Nome'] == row['Nome']) &
        (weekly_data['Semana'] == row['Semana'])
        ]

    if len(tech_week_data) == 0:
        return pd.Series([0, row['Serviço'] + row['Gorjeta']])

    total_pagamento = tech_week_data['Pagamento Tecnico'].iloc[
        0] if 'Pagamento Tecnico' in tech_week_data.columns else 0
    total_servico = tech_week_data['Serviço'].sum()

    if total_servico == 0:
        return pd.Series([0, row['Serviço'] + row['Gorjeta']])

    try:
        pagamento = (row['Serviço'] / total_servico) * total_pagamento
        lucro = row['Serviço'] + row['Gorjeta'] - pagamento
    except:
        pagamento = 0
        lucro = row['Serviço'] + row['Gorjeta']

    return pd.Series([pagamento, lucro])


def calcular_pagamento_semanal(row):
    """Calcula o pagamento semanal baseado na categoria"""
    categoria = row['Categoria']
    servico = row['Serviço']
    gorjeta = row['Gorjeta']
    dias_trabalhados = row['Dias Trabalhados']

    if categoria == 'Registering':
        pagamento = 0.00
        lucro = servico + gorjeta
    elif categoria in ['Technician', 'Started']:
        pagamento = servico * 0.20 + gorjeta
        lucro = servico * 0.80
    elif categoria == 'Training':
        pagamento = 80 * dias_trabalhados  # $80 por dia trabalhado
        lucro = servico + gorjeta - pagamento
    elif categoria == 'Coordinator':
        pagamento = servico * 0.25 + gorjeta
        lucro = servico * 0.75
    else:
        pagamento = 0
        lucro = servico + gorjeta

    return pd.Series([pagamento, lucro])
