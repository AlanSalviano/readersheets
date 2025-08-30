import streamlit as st
import pandas as pd
from datetime import date
from .utils import format_currency

def calculate_service_value(row):
    """
    Calcula o valor do serviço com base na descrição e no valor atual do serviço.
    Se o valor do serviço for mais de $10 abaixo do valor cheio, ele é ajustado para o valor cheio.
    A coluna a ser verificada é 'Total'.
    """
    description = str(row.get('Description', ''))
    current_service_value = row.get('Total', 0)

    if "01- Dog Cleaning - Small - Under 30 Lbs" in description or "Dental Under 40 LBS" in description:
        return 180 if current_service_value < 170 else current_service_value
    elif "02- Dog Cleaning - Medium - 31 to 70 Lbs" in description:
        return 210 if current_service_value < 200 else current_service_value
    elif "03- Dog Cleaning - Max - 71 to 1000 Lbs" in description or "03- Dog Cleaning - Max - 71 to 100 Lbs" in description:
        return 240 if current_service_value < 230 else current_service_value
    elif "04- Dog Cleaning - Ultra - Above 101 Lbs" in description:
        return 270 if current_service_value < 260 else current_service_value
    elif "05- Cat Cleaning" in description:
        return 210 if current_service_value < 200 else current_service_value
    elif "Nail Clipping" in description:
        return 10
    else:
        return current_service_value

def franchises_page():
    """Conteúdo da nova página 'Franchises'."""
    st.title("Franchises")
    st.write("Análise e métricas para franquias.")
    
    # Adicionando estilo para as caixas de métricas e tabela
    st.markdown("""
        <style>
            .franchise-metric-box {
                background-color: #f0f2f6;
                border-radius: 8px;
                padding: 10px;
                margin-bottom: 10px;
            }
            .franchise-metric-value {
                font-size: 1.1rem;
                font-weight: 600;
            }
            /* Estilo para campos de texto fixos com fundo preto e fonte branca */
            div[data-testid*="stTextInput-fixed-item-"] input {
                background-color: black !important;
                color: white !important;
            }
            /* Ajuste para checkbox alinhar e aumentar o tamanho */
            [data-testid="stCheckbox"] {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%; /* Garante que o checkbox ocupe toda a altura da célula */
            }
            [data-testid="stCheckbox"] input[type="checkbox"] {
                transform: scale(1.15); /* Aumenta o tamanho do checkbox em 15% */
            }
        </style>
    """, unsafe_allow_html=True)


    if 'franchises' not in st.session_state:
        st.session_state.franchises = [{
            'id': 0,
            'name': '',
            'month': 'Janeiro',
            'uploaded_files': None,
            'royalty_rate': 6.0,
            'marketing_rate': 1.0,
            'total_servicos_valor': 0,
            'calculation_rows': [
                {"Item": "Royalty Fee", "Description": "", "Qty": 0, "Unit_price": 0, "Amount": 0, "verified": False},
                {"Item": "Marketing Fee", "Description": "", "Qty": 0, "Unit_price": 0, "Amount": 0, "verified": False},
                {"Item": "Software Fee", "Description": "", "Qty": 1, "Unit_price": 350.00, "Amount": 0, "verified": False},
                {"Item": "Call Center Fee", "Description": "", "Qty": 1, "Unit_price": 1200, "Amount": 0, "verified": False},
                {"Item": "Call Center Fee Extra", "Description": "", "Qty": 0, "Unit_price": 600, "Amount": 0, "verified": False},
            ]
        }]
    
    # Lista de meses para o dropdown
    months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

    # Callback para adicionar um novo container de franquia
    def add_franchise():
        new_id = st.session_state.franchises[-1]['id'] + 1
        st.session_state.franchises.append({
            'id': new_id,
            'name': '',
            'month': months[date.today().month - 1],
            'uploaded_files': None,
            'royalty_rate': 6.0,
            'marketing_rate': 1.0,
            'total_servicos_valor': 0,
            'calculation_rows': [
                {"Item": "Royalty Fee", "Description": "", "Qty": 0, "Unit_price": 0, "Amount": 0, "verified": False},
                {"Item": "Marketing Fee", "Description": "", "Qty": 0, "Unit_price": 0, "Amount": 0, "verified": False},
                {"Item": "Software Fee", "Description": "", "Qty": 1, "Unit_price": 350.00, "Amount": 0, "verified": False},
                {"Item": "Call Center Fee", "Description": "", "Qty": 1, "Unit_price": 1200, "Amount": 0, "verified": False},
                {"Item": "Call Center Fee Extra", "Description": "", "Qty": 0, "Unit_price": 600, "Amount": 0, "verified": False},
            ]
        })

    # Callback para deletar um container de franquia
    def delete_franchise(franchise_id):
        st.session_state.franchises = [f for f in st.session_state.franchises if f['id'] != franchise_id]
        
    def add_calculation_row(franchise_id):
        for franchise in st.session_state.franchises:
            if franchise['id'] == franchise_id:
                franchise['calculation_rows'].append({"Item": "", "Description": "", "Qty": 0, "Unit_price": 0, "Amount": 0, "verified": False})
                break
    
    def delete_calculation_row(franchise_id, row_index):
        for franchise in st.session_state.franchises:
            if franchise['id'] == franchise_id:
                # Não permite deletar as 5 primeiras linhas fixas
                if row_index >= 5:
                    del franchise['calculation_rows'][row_index]
                    break

    # Exibe os containers de franquia
    for i, franchise_data in enumerate(st.session_state.franchises):
        with st.container(border=True):
            cols_inputs = st.columns([0.4, 0.4, 0.2])
            
            with cols_inputs[0]:
                franchise_data['name'] = st.text_input("Nome da Franquia", key=f"name_{franchise_data['id']}", value=franchise_data['name'])
            
            with cols_inputs[1]:
                current_month_index = months.index(franchise_data['month'])
                franchise_data['month'] = st.selectbox("Mês do Relatório", options=months, index=current_month_index, key=f"month_{franchise_data['id']}")
            
            with cols_inputs[2]:
                if len(st.session_state.franchises) > 1:
                    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
                    st.button("Deletar Franquia", key=f"delete_franchise_{franchise_data['id']}", on_click=delete_franchise, args=(franchise_data['id'],))

            st.markdown("---")
            
            # Layout minimalista para upload e métricas
            cols_upload_metrics = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])

            with cols_upload_metrics[0]:
                uploaded_files = st.file_uploader(
                    "Upload Arquivo(s)",
                    type=["csv", "xlsx"],
                    accept_multiple_files=True,
                    key=f"uploader_{franchise_data['id']}",
                    label_visibility="collapsed"
                )
            
            with cols_upload_metrics[1]:
                st.markdown('<div style="margin-top: -15px;"></div>', unsafe_allow_html=True)
                royalty_rate = st.number_input("Royalty Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=franchise_data['royalty_rate'],
                    step=0.1,
                    format="%.2f",
                    key=f"royalty_rate_{franchise_data['id']}"
                )
                franchise_data['royalty_rate'] = royalty_rate
            
            with cols_upload_metrics[2]:
                st.markdown('<div style="margin-top: -15px;"></div>', unsafe_allow_html=True)
                marketing_rate = st.number_input("Marketing Rate (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=franchise_data['marketing_rate'],
                    step=0.1,
                    format="%.2f",
                    key=f"marketing_rate_{franchise_data['id']}"
                )
                franchise_data['marketing_rate'] = marketing_rate

            if uploaded_files:
                all_dfs = []
                for uploaded_file in uploaded_files:
                    try:
                        if uploaded_file.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_file)
                        elif uploaded_file.name.endswith('.xlsx'):
                            df = pd.read_excel(uploaded_file)
                        
                        all_dfs.append(df)
                        
                    except Exception as e:
                        st.error(f"Erro ao processar o arquivo '{uploaded_file.name}': {e}")
                
                if all_dfs:
                    combined_df = pd.concat(all_dfs, ignore_index=True)

                    required_columns = ['Description', 'Total']
                    if all(col in combined_df.columns for col in required_columns):
                        
                        # Filtra a linha 'Grand Total' para não ser contabilizada
                        combined_df = combined_df[combined_df['Ticket ID'] != 'Grand Total']

                        # Limpa a coluna 'Total' e a converte para numérica
                        combined_df['Total'] = pd.to_numeric(
                            combined_df['Total'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
                            errors='coerce'
                        ).fillna(0)

                        # Aplica a lógica de cálculo
                        combined_df['Total_Calculado'] = combined_df.apply(calculate_service_value, axis=1)

                        total_pets = len(combined_df)
                        total_servicos_count = len(combined_df)
                        total_servicos_valor = combined_df['Total_Calculado'].sum()
                        franchise_data['total_servicos_valor'] = total_servicos_valor

                        # Exibição das métricas
                        st.markdown("<br>", unsafe_allow_html=True)
                        cols_metrics = st.columns(4)
                        with cols_metrics[0]:
                            st.markdown(f"<div class='franchise-metric-box'>Pets Realizados<p class='franchise-metric-value'>{total_pets}</p></div>", unsafe_allow_html=True)
                        with cols_metrics[1]:
                            st.markdown(f"<div class='franchise-metric-box'>Serviços Realizados<p class='franchise-metric-value'>{total_servicos_count}</p></div>", unsafe_allow_html=True)
                        with cols_metrics[2]:
                            st.markdown(f"<div class='franchise-metric-box'>Valor Total<p class='franchise-metric-value'>{format_currency(total_servicos_valor)}</p></div>", unsafe_allow_html=True)
                        
                        # Calcula a soma dos valores da coluna Amount
                        total_amount = sum(row['Amount'] for row in franchise_data['calculation_rows'])
                        with cols_metrics[3]:
                            st.markdown(f"<div class='franchise-metric-box'>Total Tabela<p class='franchise-metric-value'>{format_currency(total_amount)}</p></div>", unsafe_allow_html=True)
                        
                        st.markdown("---")
                        
                        st.subheader("Tabela de Cálculo")
                        
                        # Exibe o cabeçalho da tabela
                        cols_header = st.columns([0.25, 0.2, 0.15, 0.15, 0.15, 0.05, 0.05])
                        headers = ["Item", "Description", "Qty / %", "Unit price", "Amount", ""]
                        for col, header in zip(cols_header, headers):
                            col.markdown(f"**{header}**")
                        
                        # Exibe as linhas da tabela
                        for row_index, row_data in enumerate(franchise_data['calculation_rows']):
                            cols_row = st.columns([0.25, 0.2, 0.15, 0.15, 0.15, 0.05, 0.05])
                            
                            is_fixed_item = row_data['Item'] in ["Royalty Fee", "Marketing Fee", "Software Fee", "Call Center Fee", "Call Center Fee Extra"]
                            
                            with cols_row[0]:
                                item_label = "Item"
                                # Usando um key_prefix para aplicar o estilo
                                key_prefix = "fixed-item-" if is_fixed_item else ""
                                st.text_input(item_label, 
                                                key=f"item_{key_prefix}{franchise_data['id']}_{row_index}", 
                                                value=row_data['Item'], 
                                                label_visibility="collapsed", 
                                                disabled=is_fixed_item)

                            with cols_row[1]:
                                row_data['Description'] = st.text_input("Description", key=f"desc_{franchise_data['id']}_{row_index}", value=row_data['Description'], label_visibility="collapsed")
                            with cols_row[2]:
                                if row_data['Item'] == "Royalty Fee":
                                    qty_value = royalty_rate
                                    is_disabled = True
                                elif row_data['Item'] == "Marketing Fee":
                                    qty_value = marketing_rate
                                    is_disabled = True
                                elif row_data['Item'] in ["Software Fee", "Call Center Fee"]:
                                    qty_value = 1
                                    is_disabled = False
                                else:
                                    qty_value = row_data['Qty']
                                    is_disabled = False
                                    
                                style_class = "red-text" if float(qty_value) == 0 else ""

                                try:
                                    row_data['Qty'] = st.text_input("Qty", key=f"qty_{franchise_data['id']}_{row_index}", value=f"{qty_value:.2f}", label_visibility="collapsed", disabled=is_disabled)
                                    row_data['Qty'] = float(row_data['Qty'])
                                except ValueError:
                                    row_data['Qty'] = 0.0
                                
                            with cols_row[3]:
                                is_disabled = False
                                unit_price_value = row_data['Unit_price']
                                if row_data['Item'] in ["Royalty Fee", "Marketing Fee"]:
                                    unit_price_value = franchise_data['total_servicos_valor']
                                    is_disabled = True
                                elif row_data['Item'] == "Software Fee":
                                    # Substitui o text_input por um selectbox
                                    options = [0.00, 250.00, 350.00]
                                    try:
                                        index = options.index(row_data['Unit_price'])
                                    except ValueError:
                                        index = 0
                                    row_data['Unit_price'] = st.selectbox("Unit price", options, index=index, key=f"unit_price_{franchise_data['id']}_{row_index}", label_visibility="collapsed")
                                    is_disabled = False
                                elif row_data['Item'] == "Call Center Fee":
                                    unit_price_value = 1200.00
                                    is_disabled = True
                                elif row_data['Item'] == "Call Center Fee Extra":
                                    unit_price_value = 600.00
                                    is_disabled = True
                                else:
                                    unit_price_value = row_data['Unit_price']
                                    is_disabled = False
                                
                                if row_data['Item'] not in ["Software Fee"]:
                                    try:
                                        row_data['Unit_price'] = st.text_input("Unit price", key=f"unit_price_{franchise_data['id']}_{row_index}", value=f"{unit_price_value:.2f}", label_visibility="collapsed", disabled=is_disabled)
                                        row_data['Unit_price'] = float(row_data['Unit_price'])
                                    except ValueError:
                                        row_data['Unit_price'] = 0.0
                            with cols_row[4]:
                                if row_data['Item'] in ["Royalty Fee", "Marketing Fee"]:
                                    # Para os campos de taxa, multiplique a taxa decimal
                                    row_data['Amount'] = (row_data['Qty'] / 100) * row_data['Unit_price']
                                else:
                                    row_data['Amount'] = row_data['Qty'] * row_data['Unit_price']
                                st.text_input("Amount", key=f"amount_{franchise_data['id']}_{row_index}", value=f"{row_data['Amount']:.2f}", disabled=True, label_visibility="collapsed")
                            
                            with cols_row[5]:
                                if row_index >= 5:
                                    st.button("🗑️", key=f"delete_row_{franchise_data['id']}_{row_index}", on_click=delete_calculation_row, args=(franchise_data['id'], row_index))
                            
                            with cols_row[6]:
                                row_data['verified'] = st.checkbox("Verificado", value=row_data.get('verified', False), key=f"checkbox_{franchise_data['id']}_{row_index}", label_visibility="collapsed")

                        # Linha de total
                        st.button("Adicionar nova linha", key=f"add_row_{franchise_data['id']}", on_click=add_calculation_row, args=(franchise_data['id'],))
                        
                    else:
                        st.error(f"Um ou mais arquivos não contêm as colunas necessárias: {', '.join(required_columns)}")
            
        st.button("Adicionar franquia", on_click=add_franchise, key=f"add_franchise_main_{i}")
        st.markdown("---")