import pandas as pd
import numpy as np
from io import BytesIO
import requests
import streamlit as st
from .config import INVALID_CLIENTS, FORMAS_PAGAMENTO_VALIDAS

def process_spreadsheet(file):
    """
    Processa um ficheiro de planilha Excel para extrair dados financeiros.
    Aceita um objeto de ficheiro ou uma URL direta.
    """
    all_weeks_data = {}
    
    # Lida com URLs e ficheiros carregados
    if isinstance(file, str) and file.startswith('http'):
        try:
            response = requests.get(file)
            file = BytesIO(response.content)
        except requests.exceptions.RequestException as e:
            st.error(f"Erro ao carregar planilha do URL: {e}")
            return pd.DataFrame()
    elif isinstance(file, BytesIO):
        file.seek(0)
    
    try:
        xls = pd.ExcelFile(file)
    except Exception as e:
        st.warning(f"Não foi possível ler o ficheiro Excel. Verifique se ele não está corrompido ou vazio. Erro: {e}")
        return pd.DataFrame()

    for sheet_name in xls.sheet_names:
        if sheet_name.startswith('WEEK'):
            try:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
            except Exception as e:
                st.warning(f"Erro ao ler a folha '{sheet_name}'. Ignorando... Erro: {e}")
                continue

            # Se a planilha estiver vazia, ignora-a.
            if df.empty:
                st.info(f"A folha '{sheet_name}' está vazia e será ignorada.")
                continue

            technician_blocks = []
            current_block = []
            collecting = False
            for idx, row in df.iterrows():
                if any('NAME:' in str(cell) for cell in row.values):
                    if current_block:
                        technician_blocks.append(current_block)
                        current_block = []
                    collecting = True
                if collecting:
                    current_block.append(row)
            if current_block:
                technician_blocks.append(current_block)

            week_data = []
            for block in technician_blocks:
                name_row = next((row for row in block if any('NAME:' in str(cell) for cell in row.values)), None)

                if name_row is None:
                    continue
                
                # Procura a coluna "NAME:" para garantir que o acesso é seguro
                name_col_idx = -1
                for i, cell in enumerate(name_row.values):
                    if isinstance(cell, str) and 'NAME:' in cell:
                        name_col_idx = i
                        break
                
                if name_col_idx == -1 or len(name_row) <= name_col_idx + 1:
                    continue

                technician_info = {
                    'Semana': sheet_name,
                    'Nome': name_row[name_col_idx + 1] if len(name_row) > name_col_idx + 1 else None,
                    'Categoria': name_row[name_col_idx + 3] if len(name_row) > name_col_idx + 3 else None,
                    'Origem': name_row[name_col_idx + 5] if len(name_row) > name_col_idx + 5 and 'From:' in str(
                        name_row[name_col_idx + 4]) else None
                }

                header_row_idx = next((i for i, row in enumerate(block) if all(
                    keyword in str(row.values) for keyword in ['Schedule', 'DATE', 'SERVICE'])), None)
                if header_row_idx is None:
                    continue

                days_data = []
                for i in range(header_row_idx + 1, len(block)):
                    day_row = block[i]
                    for day_idx, day_col in enumerate(
                            [(1, 9), (10, 18), (19, 27), (28, 36), (37, 45), (46, 54), (55, 63)]):
                        start_col, end_col = day_col
                        # Garante que as colunas existem antes de aceder
                        if len(day_row) <= end_col:
                            continue
                        
                        day_data = day_row[start_col:end_col + 1].values
                        client_name = str(day_data[0]).strip() if pd.notna(day_data[0]) else ''

                        if not client_name or client_name.upper() in [c.upper() for c in INVALID_CLIENTS]:
                            continue
                        
                        # Verifica se a coluna de serviço e gorjeta existem
                        if len(day_data) > 2 and pd.notna(day_data[2]) and str(day_data[2]).strip() and str(day_data[2]).strip() != 'nan':
                            try:
                                service_value = float(day_data[2])
                            except (ValueError, TypeError):
                                service_value = np.nan
                            
                            if not np.isnan(service_value):
                                pagamento = day_data[5] if len(day_data) > 5 and pd.notna(day_data[5]) and str(
                                    day_data[5]).strip() in FORMAS_PAGAMENTO_VALIDAS else None
                                tip_value = float(day_data[3]) if len(day_data) > 3 and pd.notna(day_data[3]) else 0
                                day_info = {
                                    'Dia': ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][
                                        day_idx],
                                    'Data': day_data[1],
                                    'Cliente': client_name,
                                    'Serviço': service_value,
                                    'Gorjeta': tip_value,
                                    'Pets': day_data[4] if len(day_data) > 4 and pd.notna(day_data[4]) else 0,
                                    'Pagamento': pagamento,
                                    'ID Pagamento': day_data[6] if len(day_data) > 6 and pd.notna(day_data[6]) else None,
                                    'Verificado': day_data[7] if len(day_data) > 7 and pd.notna(day_data[7]) else False,
                                    'Realizado': True
                                }
                                days_data.append({**technician_info, **day_info})
                        elif pd.notna(day_data[0]):
                            if client_name.upper() in [c.upper() for c in INVALID_CLIENTS]:
                                continue
                            day_info = {
                                'Dia': ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'][day_idx],
                                'Data': day_data[1],
                                'Cliente': client_name,
                                'Serviço': 0,
                                'Gorjeta': 0,
                                'Pets': 0,
                                'Pagamento': None,
                                'ID Pagamento': None,
                                'Verificado': False,
                                'Realizado': False
                            }
                            days_data.append({**technician_info, **day_info})

                week_data.extend(days_data)
            if week_data:
                all_weeks_data[sheet_name] = pd.DataFrame(week_data)

    if all_weeks_data:
        combined_data = pd.concat(all_weeks_data.values(), ignore_index=True)
        combined_data['Data'] = pd.to_datetime(combined_data['Data'], errors='coerce')
        combined_data['Serviço'] = pd.to_numeric(combined_data['Serviço'], errors='coerce')
        combined_data['Gorjeta'] = pd.to_numeric(combined_data['Gorjeta'], errors='coerce').fillna(0)
        combined_data['Pets'] = pd.to_numeric(combined_data['Pets'], errors='coerce').fillna(0)
        combined_data = combined_data.dropna(subset=['Data'])
        combined_data = combined_data[
            ~combined_data['Cliente'].astype(str).str.strip().str.upper().isin([c.upper() for c in INVALID_CLIENTS])]
        return combined_data
    
    st.warning("Nenhum dado válido foi encontrado nas planilhas processadas.")
    return pd.DataFrame()
