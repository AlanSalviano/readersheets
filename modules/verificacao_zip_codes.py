import streamlit as st
import requests
import json
import os

# Nome do arquivo para salvar os dados
DATA_FILE = "tech_cidades.json"

def save_tech_data(data):
    """Salva os dados de técnicos e cidades em um arquivo JSON."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_tech_data():
    """Carrega os dados de técnicos e cidades do arquivo JSON."""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    return []

def delete_row(index):
    """Callback para deletar uma linha da tabela."""
    if len(st.session_state.tech_data) > 1:
        st.session_state.tech_data.pop(index)
        st.rerun()

def add_new_row():
    """Callback para adicionar uma nova linha à tabela."""
    st.session_state.tech_data.append({"nome": "", "cidades": []})

def zip_code_page():
    """
    Renderiza a página para verificar a região de um CEP e para cadastrar técnicos.
    """
    st.title("Verificação de Zip Codes e Cadastro de Técnicos")
    st.markdown("---")
    
    # Seção de Verificação de Zip Codes
    st.subheader("Verificação de Zip Codes")
    zip_code = st.text_input("Insira um Zip Code (EUA):", max_chars=5)
    
    if st.button("Verificar"):
        if zip_code:
            try:
                # API pública para consulta de CEPs dos EUA
                url = f"http://api.zippopotam.us/us/{zip_code}"
                response = requests.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    place = data['places'][0]
                    city = place['place name']
                    state = place['state abbreviation']
                    
                    st.success(f"**Zip Code Encontrado!**")
                    st.write(f"**Cidade:** {city}")
                    st.write(f"**Estado:** {state}")
                    
                    # --- Nova lógica para encontrar e exibir técnicos disponíveis ---
                    tech_data = load_tech_data()
                    disponiveis = []
                    for tech_entry in tech_data:
                        cidades_do_tecnico = tech_entry.get('cidades', [])
                        if isinstance(cidades_do_tecnico, list):
                            if city in cidades_do_tecnico:
                                disponiveis.append(tech_entry['nome'])
                    
                    st.write(f"**Técnicos disponíveis:** {', '.join(disponiveis) if disponiveis else 'Nenhum'}")
                    # --- Fim da nova lógica ---
                    
                elif response.status_code == 404:
                    st.error("Zip Code não encontrado. Por favor, verifique o número e tente novamente.")
                else:
                    st.error(f"Erro na busca: Código {response.status_code}")
            
            except requests.exceptions.RequestException:
                st.error("Erro de conexão. Por favor, verifique sua internet ou a URL da API.")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")
        else:
            st.warning("Por favor, insira um Zip Code para continuar.")

    # Seção de Cadastro de Técnicos
    st.markdown("---")
    st.subheader("Cadastro de Técnicos e Cidades")
    
    if 'tech_data' not in st.session_state:
        saved_data = load_tech_data()
        st.session_state.tech_data = saved_data if saved_data else [{"nome": "", "cidades": []}]
            
    st.info("Insira o nome do técnico e as cidades onde ele realiza atendimentos. Você pode adicionar novas cidades digitando no campo e pressionando Enter.")

    header_cols = st.columns([0.4, 0.5, 0.1])
    with header_cols[0]:
        st.markdown("**Nome do Técnico**")
    with header_cols[1]:
        st.markdown("**Cidades de Atendimento**")
    with header_cols[2]:
        st.markdown("**Excluir**")

    for i, entry in enumerate(st.session_state.tech_data):
        cols = st.columns([0.4, 0.5, 0.1])
        
        with cols[0]:
            entry["nome"] = st.text_input(
                "Nome", 
                value=entry.get("nome", ""), 
                key=f"tech_name_{i}", 
                label_visibility="collapsed"
            )
        
        with cols[1]:
            # Este campo serve para adicionar novas cidades
            new_city = st.text_input(
                "Adicionar cidade", 
                key=f"add_city_{i}", 
                placeholder="Digite a cidade e pressione Enter...",
                label_visibility="collapsed"
            )
            if new_city:
                if new_city not in entry["cidades"]:
                    entry["cidades"].append(new_city.strip())
                    st.rerun()

            # O multiselect exibe as cidades como tags
            entry["cidades"] = st.multiselect(
                "Cidades",
                options=entry["cidades"],
                default=entry["cidades"],
                key=f"tech_cities_{i}",
                label_visibility="collapsed"
            )
        
        with cols[2]:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if len(st.session_state.tech_data) > 1:
                if st.button("🗑️", key=f"delete_btn_{i}"):
                    delete_row(i)

    st.markdown("---")
    col_buttons = st.columns([0.25, 0.25, 0.5])
    with col_buttons[0]:
        if st.button("Adicionar nova linha"):
            add_new_row()
    with col_buttons[1]:
        if st.button("Salvar"):
            save_tech_data(st.session_state.tech_data)
            st.success("Dados salvos com sucesso!")
