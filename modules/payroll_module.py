import streamlit as st
import pandas as pd
import json
import os
from modules.utils import format_currency

# Nome do arquivo para salvar as configurações
SETTINGS_FILE = "payroll_settings.json"

def save_payroll_settings(settings):
    """Salva as configurações do payroll em um arquivo JSON."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

def load_payroll_settings():
    """Carrega as configurações salvas do payroll."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def payroll_page(data):
    """
    Função que renderiza a página de Payroll.
    """
    st.title("Payroll dos Técnicos")

    # Adiciona um CSS para ajustar o tamanho da fonte dos números do st.metric
    # e para estilizar a tabela
    st.markdown("""
        <style>
            [data-testid="stMetricValue"] {
                font-size: 1.2rem;
            }
            .st-emotion-cache-1r6ch5c div:first-child .stMarkdown {
                margin-bottom: 0.5rem;
            }
            .header-cell {
                background-color: white;
                color: black;
                font-weight: bold;
                padding: 10px;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 0.8rem;
            }
            .data-row {
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .data-cell {
                padding: 10px;
                text-align: center;
                flex: 1;
            }
            .st-emotion-cache-13k623y > div {
                padding: 0;
                gap: 0;
            }
        </style>
    """, unsafe_allow_html=True)

    # Filtra apenas os serviços realizados
    completed_services = data[data['Realizado']]
    
    if completed_services.empty:
        st.info("Nenhum serviço realizado encontrado para o período selecionado.")
        return

    # Calcula o Valor Produzido (Serviços + Gorjetas) por técnico
    payroll_summary = completed_services.groupby(['Nome', 'Categoria']).agg(
        Total_Servicos=('Serviço', 'sum'),
        Total_Gorjetas=('Gorjeta', 'sum'),
        Total_Pets=('Pets', 'sum'),
        Total_Atendimentos=('Cliente', 'count')
    ).reset_index()

    payroll_summary['Valor_Produzido'] = payroll_summary['Total_Servicos'] + payroll_summary['Total_Gorjetas']
    
    st.subheader("Resumo do Payroll por Técnico")
    
    # Carrega as configurações salvas
    saved_settings = load_payroll_settings()
    
    # Cria uma lista para armazenar os dados de cada técnico
    payroll_data = []
    
    # Lista para salvar as novas configurações
    current_settings = {}

    # Cria as colunas para os cabeçalhos de forma mais clara
    col_headers = st.columns(10)
    headers = [
        "Técnico", "Pets", "Atendimentos", "Produzido", "Comissão (%)",
        "Pagamento Base", "Pagamento Fixo", "Variáveis", "Pagamento Final", "Support Value"
    ]
    for col, header in zip(col_headers, headers):
        with col:
            st.markdown(f'<div class="header-cell">{header}</div>', unsafe_allow_html=True)

    # Valores pré-definidos para a selectbox de pagamento fixo
    PAYMENT_OPTIONS = ["Selecionar ou digitar", 750.00, 900.00]
    COMMISSION_OPTIONS = [20, 25]
    FIXED_PAYMENT_OPTIONS = ["Selecionar", 750.00, 900.00]

    # Itera sobre cada técnico para criar os campos personalizados
    for index, row in payroll_summary.iterrows():
        tech_name = row['Nome']
        categoria = row['Categoria']
        valor_produzido = row['Valor_Produzido']
        total_servicos = row['Total_Servicos']
        total_gorjetas = row['Total_Gorjetas']
        total_pets = row['Total_Pets']
        total_atendimentos = row['Total_Atendimentos']
        
        # Cria as colunas para os inputs de cada técnico
        cols = st.columns(10)

        with cols[0]:
            display_name = tech_name[:15] + '...' if len(tech_name) > 15 else tech_name
            st.markdown(f'<div class="data-row" style="font-size: 0.8rem;"><b>{display_name}</b></div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f'<div class="data-row">{total_pets}</div>', unsafe_allow_html=True)
            
        with cols[2]:
            st.markdown(f'<div class="data-row">{total_atendimentos}</div>', unsafe_allow_html=True)
            
        with cols[3]:
            st.markdown(f'<div class="data-row">{format_currency(valor_produzido)}</div>', unsafe_allow_html=True)
        
        with cols[4]:
            # Lógica para definir o padrão da comissão
            default_commission_index = 0
            if categoria == "Coordinator":
                try:
                    default_commission_index = COMMISSION_OPTIONS.index(25)
                except ValueError:
                    default_commission_index = 0
            
            # Tenta carregar o valor salvo, se existir
            saved_commission = saved_settings.get(tech_name, {}).get('comissao')
            if saved_commission:
                try:
                    default_commission_index = COMMISSION_OPTIONS.index(saved_commission)
                except ValueError:
                    default_commission_index = 0

            comissao_porcentagem = st.selectbox(
                "Comissão",
                COMMISSION_OPTIONS,
                key=f"comissao_{tech_name}",
                label_visibility="collapsed",
                index=default_commission_index
            )

        # Cálculo do pagamento base
        pagamento_base = total_servicos * (comissao_porcentagem / 100) + total_gorjetas

        with cols[5]:
            st.markdown(f'<div class="data-row">{format_currency(pagamento_base)}</div>', unsafe_allow_html=True)
            
        with cols[6]:
            # Lógica para definir o padrão do pagamento fixo
            default_fixed_index = 0
            if categoria == "Starter":
                try:
                    default_fixed_index = FIXED_PAYMENT_OPTIONS.index(900.00)
                except ValueError:
                    default_fixed_index = 0
            
            # Tenta carregar o valor salvo, se existir
            saved_fixed_payment = saved_settings.get(tech_name, {}).get('pagamento_fixo')
            if saved_fixed_payment:
                try:
                    default_fixed_index = FIXED_PAYMENT_OPTIONS.index(saved_fixed_payment)
                except ValueError:
                    default_fixed_index = 0
            
            # Selecionar pagamento fixo
            pagamento_fixo = st.selectbox(
                "Fixo",
                FIXED_PAYMENT_OPTIONS,
                key=f"pagamento_fixo_{tech_name}",
                label_visibility="collapsed",
                index=default_fixed_index
            )
            
            # Lógica para usar o pagamento fixo ou o pagamento base
            pagamento_para_calculo = pagamento_fixo if pagamento_fixo != "Selecionar" else pagamento_base

        with cols[7]:
            # Campo para o usuário adicionar variáveis (opcional)
            variaveis = st.number_input(
                "Valor",
                value=0.0,
                format="%.2f",
                key=f"variaveis_{tech_name}",
                label_visibility="collapsed"
            )

        # Cálculo do pagamento final
        pagamento_final = pagamento_para_calculo + variaveis

        with cols[8]:
            st.markdown(f'<div class="data-row"><b>{format_currency(pagamento_final)}</b></div>', unsafe_allow_html=True)
        
        with cols[9]:
            # Lógica para o campo 'Support Value'
            support_value = 0.0
            if pagamento_final > pagamento_base:
                support_value = pagamento_final - pagamento_base
            
            st.markdown(f'<div class="data-row">{format_currency(support_value)}</div>', unsafe_allow_html=True)

        # Adiciona os dados para exportação e para salvar configurações
        payroll_data.append({
            "Técnico": tech_name,
            "Total de Pets": total_pets,
            "Total de Atendimentos": total_atendimentos,
            "Valor Produzido": valor_produzido,
            "Comissao (%)": comissao_porcentagem,
            "Pagamento Base": pagamento_base,
            "Pagamento Fixo": pagamento_fixo if pagamento_fixo != "Selecionar" else pagamento_base,
            "Variáveis": variaveis,
            "Pagamento Final": pagamento_final,
            "Support Value": (pagamento_final - pagamento_base) if pagamento_final > pagamento_base else 0
        })

        # Salva as configurações atuais para uso futuro
        current_settings[tech_name] = {
            'comissao': comissao_porcentagem,
            'pagamento_fixo': pagamento_fixo if pagamento_fixo != "Selecionar" else None
        }

    # Botão para salvar as configurações
    st.markdown("---")
    if st.button("Salvar Configurações"):
        save_payroll_settings(current_settings)
        st.success("Configurações salvas com sucesso!")

    # Criação do DataFrame final e botão de download
    st.markdown("---")
    st.subheader("Tabela de Payroll para Download")
    final_payroll_df = pd.DataFrame(payroll_data)
    
    # Exibe o DataFrame para visualização antes do download
    st.dataframe(final_payroll_df)
    
    csv = final_payroll_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📁 Baixar Payroll em CSV",
        data=csv,
        file_name="payroll_summary.csv",
        mime="text/csv"
    )
