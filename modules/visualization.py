import plotly.express as px
import pandas as pd
from .utils import format_currency


# 📈 Gráfico de evolução semanal por técnico
def plot_weekly_evolution(data):
    fig = px.line(
        data,
        x='Semana',
        y='Serviço',
        color='Nome',
        markers=True,
        title='Evolução de Serviços por Técnico',
        labels={'Serviço': 'Valor em Serviços ($)', 'Semana': 'Semana'}
    )
    fig.update_traces(hovertemplate="<b>%{x}</b><br>Valor: $%{y:,.2f}")
    return fig


# 💰 Gráfico de pagamento semanal por técnico
def plot_weekly_payments(data):
    fig = px.bar(
        data.sort_values('Pagamento Tecnico'),
        x='Pagamento Tecnico',
        y='Nome',
        color='Semana',
        barmode='group',
        title='Pagamento Semanal por Técnico',
        labels={'Pagamento Tecnico': 'Pagamento ($)', 'Nome': 'Técnico'}
    )
    fig.update_traces(
        texttemplate='$%{x:,.2f}',
        textposition='outside'
    )
    fig.update_layout(hovermode="x unified")
    return fig


# 👩‍🔧 Gráfico de atendimentos por técnico
def plot_services_by_tech(data):
    fig = px.bar(
        data.sort_values('Atendimentos'),
        x='Atendimentos',
        y='Nome',
        title='Atendimentos por Técnico',
        color='Categoria',
        labels={'Atendimentos': 'Quantidade', 'Nome': 'Técnico'}
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Atendimentos: %{x}<br>Categoria: %{marker.color}"
    )
    return fig


# 💵 Gráfico de gorjetas por técnico
def plot_tips_by_tech(data):
    fig = px.bar(
        data.sort_values('Gorjeta'),
        x='Gorjeta',
        y='Nome',
        title='Gorjetas por Técnico',
        color='Categoria',
        labels={'Gorjeta': 'Valor Gorjetas ($)', 'Nome': 'Técnico'}
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Total Gorjetas: $%{x:,.2f}<br>Categoria: %{marker.color}"
    )
    return fig


# 📆 Gráfico de atendimentos por dia da semana
def plot_services_by_day(data):
    fig = px.bar(
        data,
        x='Dia',
        y='Atendimentos',
        title='Atendimentos por Dia da Semana',
        labels={'Atendimentos': 'Quantidade'}
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>Atendimentos: %{y}"
    )
    return fig


# 💳 Gráfico de valor total por método de pagamento
def plot_payment_methods_total(data):
    fig = px.bar(
        data.sort_values('Total'),
        x='Total',
        y='Pagamento',
        title='Valor Total por Método de Pagamento (Serviços + Gorjetas)',
        color='Serviço',
        color_continuous_scale='Peach',
        labels={'Total': 'Valor Total ($)', 'Serviço': 'Valor Serviços ($)'}
    )
    fig.update_traces(
        hovertemplate="<b>%{y}</b><br>Total: $%{x:,.2f}<br>Serviços: $%{marker.color:,.2f}"
    )
    return fig


# 📊 Gráfico de quantidade de usos por método de pagamento
def plot_payment_methods_usage(data):
    if 'Percentual Uso' not in data.columns:
        data['Percentual Uso'] = (data['Qtd Usos'] / data['Qtd Usos'].sum() * 100).round(2)

    fig = px.bar(
        data.sort_values('Qtd Usos'),
        x='Qtd Usos',
        y='Pagamento',
        title='Quantidade de Usos por Método de Pagamento',
        color='Qtd Usos',
        color_continuous_scale='Peach',
        labels={'Qtd Usos': 'Quantidade de Usos'},
        text='Percentual Uso'
    )
    fig.update_traces(
        texttemplate='%{text}%',
        textposition='outside',
        hovertemplate="<b>%{y}</b><br>Usos: %{x}<br>% do Total: %{text}%"
    )
    return fig
