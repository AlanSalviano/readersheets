import streamlit as st
import pandas as pd
import json
import os
from modules.utils import format_currency
from modules.payroll_pdf_generator import create_payroll_summary_with_vars_pdf
from modules.pdf_generator import create_pdf, create_tech_payment_receipt, create_technician_of_the_week_receipt

# Nome do arquivo para salvar as configurações
SETTINGS_FILE = "payroll_settings.json"

def save_payroll_settings(settings, custom_variables):
    """Salva as configurações do payroll e as variáveis adicionais em um arquivo JSON."""
    full_settings = {
        "payroll_config": settings,
        "custom_variables": custom_variables
    }
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(full_settings, f, indent=4)

def load_payroll_settings():
    """Carrega as configurações salvas do payroll e as variáveis adicionais."""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, KeyError):
            # Retorna a estrutura padrão caso o arquivo esteja vazio ou corrompido
            return {"payroll_config": {}, "custom_variables": []}
    return {"payroll_config": {}, "custom_variables": []}

# Callback function to delete a variable row
def delete_variable_row(index):
    del st.session_state.custom_variables[index]

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
                display: flex;
                align-items: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                text-align: center;
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

    # Carrega as configurações salvas no início
    saved_data = load_payroll_settings()
    saved_settings = saved_data.get("payroll_config", {})
    saved_custom_variables = saved_data.get("custom_variables", [])

    # Inicializa o estado da sessão para as variáveis, carregando os dados salvos se existirem
    if 'custom_variables' not in st.session_state:
        if saved_custom_variables:
            st.session_state.custom_variables = saved_custom_variables
        else:
            st.session_state.custom_variables = [{'description': '', 'valor_da_parcela': 0.0, 'total_de_parcelas': 0, 'parcela_atual': 0, 'tech': ''}]

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

    # Variaveis para totalização
    total_pets_sum = 0
    total_atendimentos_sum = 0
    total_produzido_sum = 0
    total_pagamento_base_sum = 0
    total_variaveis_sum = 0
    total_pagamento_final_sum = 0
    total_support_value_sum = 0

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
            st.markdown(f'<div class="data-row" style="font-size: 0.88rem;"><b>{display_name}</b></div>', unsafe_allow_html=True)
        
        with cols[1]:
            st.markdown(f'<div class="data-row">{total_pets}</div>', unsafe_allow_html=True)
            total_pets_sum += total_pets
            
        with cols[2]:
            st.markdown(f'<div class="data-row">{total_atendimentos}</div>', unsafe_allow_html=True)
            total_atendimentos_sum += total_atendimentos
            
        with cols[3]:
            st.markdown(f'<div class="data-row">{format_currency(valor_produzido)}</div>', unsafe_allow_html=True)
            total_produzido_sum += valor_produzido
        
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
            # Regra para deixar a linha vermelha se o pagamento base for menor que 900
            base_style = "color: red !important;" if pagamento_base < 900 else ""
            st.markdown(f'<div class="data-row" style="{base_style}">{format_currency(pagamento_base)}</div>', unsafe_allow_html=True)
            total_pagamento_base_sum += pagamento_base
            
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
        
        # Encontra as variáveis personalizadas para o técnico atual
        custom_vars_value = sum(
            v['valor_da_parcela'] for v in st.session_state.custom_variables if v['tech'] == tech_name
        )
        
        with cols[7]:
            vars_style = "color: green !important;" if custom_vars_value > 0 else "color: red !important;" if custom_vars_value < 0 else ""
            st.markdown(f'<div class="data-row" style="{vars_style}">{format_currency(custom_vars_value)}</div>', unsafe_allow_html=True)
            total_variaveis_sum += custom_vars_value

        # Cálculo do pagamento final
        pagamento_final = pagamento_para_calculo + custom_vars_value

        with cols[8]:
            # Aplica a cor vermelha se o pagamento final for menor que 900
            final_style = "color: red !important;" if pagamento_final < 900 else ""
            st.markdown(f'<div class="data-row" style="{final_style}"><b>{format_currency(pagamento_final)}</b></div>', unsafe_allow_html=True)
            total_pagamento_final_sum += pagamento_final
        
        with cols[9]:
            # Lógica para o campo 'Support Value'
            support_value = 0.0
            if pagamento_final > pagamento_base:
                support_value = pagamento_final - pagamento_base
            
            st.markdown(f'<div class="data-row">{format_currency(support_value)}</div>', unsafe_allow_html=True)
            total_support_value_sum += support_value

        # Adiciona os dados para exportação e para salvar configurações
        payroll_data.append({
            "Técnico": tech_name,
            "Total de Pets": total_pets,
            "Total de Atendimentos": total_atendimentos,
            "Valor Produzido": valor_produzido,
            "Comissao (%)": comissao_porcentagem,
            "Pagamento Base": pagamento_base,
            "Pagamento Fixo": pagamento_fixo if pagamento_fixo != "Selecionar" else pagamento_base,
            "Variáveis": custom_vars_value,
            "Pagamento Final": pagamento_final,
            "Support Value": (pagamento_final - pagamento_base) if pagamento_final > pagamento_base else 0
        })

        # Salva as configurações atuais para uso futuro
        current_settings[tech_name] = {
            'comissao': comissao_porcentagem,
            'pagamento_fixo': pagamento_fixo if pagamento_fixo != "Selecionar" else None
        }

    # Linha de totalização
    st.markdown("---")
    cols_total = st.columns(10)
    with cols_total[0]:
        st.markdown(f'<div class="data-row"><b>Total</b></div>', unsafe_allow_html=True)
    with cols_total[1]:
        st.markdown(f'<div class="data-row"><b>{total_pets_sum}</b></div>', unsafe_allow_html=True)
    with cols_total[2]:
        st.markdown(f'<div class="data-row"><b>{total_atendimentos_sum}</b></div>', unsafe_allow_html=True)
    with cols_total[3]:
        st.markdown(f'<div class="data-row"><b>{format_currency(total_produzido_sum)}</b></div>', unsafe_allow_html=True)
    with cols_total[4]:
        st.markdown(f'<div class="data-row"></div>', unsafe_allow_html=True)
    with cols_total[5]:
        st.markdown(f'<div class="data-row"><b>{format_currency(total_pagamento_base_sum)}</b></div>', unsafe_allow_html=True)
    with cols_total[6]:
        st.markdown(f'<div class="data-row"></div>', unsafe_allow_html=True)
    with cols_total[7]:
        vars_style = "color: green !important;" if total_variaveis_sum > 0 else "color: red !important;" if total_variaveis_sum < 0 else ""
        st.markdown(f'<div class="data-row" style="{vars_style}"><b>{format_currency(total_variaveis_sum)}</b></div>', unsafe_allow_html=True)
    with cols_total[8]:
        st.markdown(f'<div class="data-row"><b>{format_currency(total_pagamento_final_sum)}</b></div>', unsafe_allow_html=True)
    with cols_total[9]:
        st.markdown(f'<div class="data-row"><b>{format_currency(total_support_value_sum)}</b></div>', unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("Variáveis Adicionais")
    st.markdown("""
        <style>
            .variable-row-container {
                padding: 10px;
                border-bottom: 1px solid #e0e0e0;
                display: flex;
                gap: 0px;
                align-items: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
        </style>
    """, unsafe_allow_html=True)
    
    # Cria o cabeçalho das variáveis
    var_headers = st.columns([0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05])
    with var_headers[0]:
        st.markdown(f'<div class="header-cell">Técnico</div>', unsafe_allow_html=True)
    with var_headers[1]:
        st.markdown(f'<div class="header-cell">Descrição da Variável</div>', unsafe_allow_html=True)
    with var_headers[2]:
        st.markdown(f'<div class="header-cell">Valor da Parcela</div>', unsafe_allow_html=True)
    with var_headers[3]:
        st.markdown(f'<div class="header-cell">Total de Parcelas</div>', unsafe_allow_html=True)
    with var_headers[4]:
        st.markdown(f'<div class="header-cell">Parcela Atual</div>', unsafe_allow_html=True)
    with var_headers[5]:
        st.markdown(f'<div class="header-cell">Dívida Total</div>', unsafe_allow_html=True)
    with var_headers[6]:
        st.markdown(f'<div class="header-cell">Dívida Paga</div>', unsafe_allow_html=True)
    with var_headers[7]:
        st.markdown(f'<div class="header-cell"></div>', unsafe_allow_html=True) # Coluna vazia para o botão

    # Itera sobre o estado da sessão para criar as linhas de variáveis
    for i in range(len(st.session_state.custom_variables)):
        cols = st.columns([0.2, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1, 0.05])
        
        with cols[0]:
            tech_options = [''] + list(payroll_summary['Nome'].unique())
            default_index = tech_options.index(st.session_state.custom_variables[i]['tech']) if st.session_state.custom_variables[i]['tech'] in tech_options else 0
            
            st.session_state.custom_variables[i]['tech'] = st.selectbox(
                "Técnico",
                options=tech_options,
                key=f"var_tech_{i}",
                label_visibility="collapsed",
                index=default_index
            )
        with cols[1]:
            st.session_state.custom_variables[i]['description'] = st.text_input(
                "Descrição",
                value=st.session_state.custom_variables[i]['description'],
                key=f"var_desc_{i}",
                label_visibility="collapsed"
            )
        with cols[2]:
            st.session_state.custom_variables[i]['valor_da_parcela'] = st.number_input(
                "Valor da Parcela",
                value=st.session_state.custom_variables[i]['valor_da_parcela'] if st.session_state.custom_variables[i]['valor_da_parcela'] >= 0 else 0.0,
                min_value=0.0,
                format="%.2f",
                key=f"var_valor_parcela_{i}",
                label_visibility="collapsed"
            )
        with cols[3]:
            st.session_state.custom_variables[i]['total_de_parcelas'] = st.number_input(
                "Total de Parcelas",
                value=st.session_state.custom_variables[i]['total_de_parcelas'] if st.session_state.custom_variables[i]['total_de_parcelas'] >= 0 else 0,
                min_value=0,
                format="%d",
                key=f"var_total_parcelas_{i}",
                label_visibility="collapsed"
            )
        with cols[4]:
            st.session_state.custom_variables[i]['parcela_atual'] = st.number_input(
                "Parcela Atual",
                value=st.session_state.custom_variables[i]['parcela_atual'] if st.session_state.custom_variables[i]['parcela_atual'] >= 0 else 0,
                min_value=0,
                format="%d",
                key=f"var_parcela_atual_{i}",
                label_visibility="collapsed"
            )
        with cols[5]:
            total_debt = st.session_state.custom_variables[i]['valor_da_parcela'] * st.session_state.custom_variables[i]['total_de_parcelas']
            st.markdown(f'<div class="data-row">{format_currency(total_debt)}</div>', unsafe_allow_html=True)
        with cols[6]:
            paid_debt = st.session_state.custom_variables[i]['valor_da_parcela'] * st.session_state.custom_variables[i]['parcela_atual']
            st.markdown(f'<div class="data-row">{format_currency(paid_debt)}</div>', unsafe_allow_html=True)
        
        with cols[7]:
            st.button("🗑️", key=f"delete_{i}", on_click=delete_variable_row, args=(i,))

    if st.button("Adicionar nova variável"):
        st.session_state.custom_variables.append({'description': '', 'valor_da_parcela': 0.0, 'total_de_parcelas': 0, 'parcela_atual': 0, 'tech': ''})

    # Painel de configurações
    st.markdown("---")
    
    # Botão para salvar as configurações
    col_buttons = st.columns([0.2, 0.8])
    with col_buttons[0]:
        if st.button("Salvar Configurações"):
            save_payroll_settings(current_settings, st.session_state.custom_variables)
            st.success("Configurações salvas com sucesso!")

    # Adicionei um novo `st.columns` para os campos de data e o botão de download do PDF
    col_pdf_buttons = st.columns([0.2, 0.2, 0.6])
    with col_pdf_buttons[0]:
        start_date = st.date_input("Data inicial", value=None)
    with col_pdf_buttons[1]:
        end_date = st.date_input("Data final", value=None)
    with col_pdf_buttons[2]:
        st.markdown("<br>", unsafe_allow_html=True) # Espaçamento para alinhar o botão com os campos de data
        # Lógica para gerar o PDF
        pdf_data = create_payroll_summary_with_vars_pdf(payroll_data, st.session_state.custom_variables, start_date, end_date)
        st.download_button(
            label="📥 Baixar PDF do Payroll",
            data=pdf_data.output(dest='S').encode('latin-1'),
            file_name="payroll_report.pdf",
            mime="application/pdf"
        )


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
