import streamlit as st
import requests
import json
import os
import math
import pandas as pd
import pydeck as pdk
import polyline

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
    st.session_state.tech_data.append({"nome": "", "zip_code": "", "cidades": []})

def get_lat_lon(zip_code):
    """Busca a latitude e longitude de um CEP usando a API Zippopotam.us."""
    try:
        url = f"http://api.zippopotam.us/us/{zip_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            place = data['places'][0]
            return float(place['latitude']), float(place['longitude'])
        else:
            return None, None
    except:
        return None, None

def get_driving_directions(api_key, origin, destination):
    """Busca a distância e o tempo de percurso entre dois pontos usando a Google Directions API."""
    try:
        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={origin}&destination={destination}&key={api_key}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'OK':
                # Pega a primeira rota e o primeiro trecho
                leg = data['routes'][0]['legs'][0]
                distance = leg['distance']['text']
                duration = leg['duration']['text']
                # Retorna o overview polyline para desenhar a rota
                polyline_encoded = data['routes'][0]['overview_polyline']['points']
                return distance, duration, polyline_encoded
            else:
                return None, None, None
        else:
            return None, None, None
    except:
        return None, None, None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calcula a distância euclidiana (em linha reta) entre duas coordenadas."""
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)


def zip_code_page():
    """
    Renderiza a página para verificar a região de um CEP e para cadastrar técnicos.
    """
    st.title("Verificação de Zip Codes e Cadastro de Técnicos")
    st.markdown("---")
    
    # Adicionar campo para a chave de API
    st.markdown("### Configurações")
    google_maps_api_key = st.text_input("Insira sua chave da Google Maps API:", type="password", value="AIzaSyCtn6nbsSgdqVrlphccWsc7jrCKYeV_FuU")

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
                    
                    # --- Lógica para encontrar e exibir técnicos disponíveis ---
                    tech_data = load_tech_data()
                    disponiveis = []
                    for tech_entry in tech_data:
                        cidades_do_tecnico = tech_entry.get('cidades', [])
                        if isinstance(cidades_do_tecnico, list):
                            if city in cidades_do_tecnico:
                                disponiveis.append(tech_entry['nome'])
                    
                    st.write(f"**Técnicos disponíveis:** {', '.join(disponiveis) if disponiveis else 'Nenhum'}")
                    # --- Fim da lógica de técnicos disponíveis ---

                    # --- Nova lógica para encontrar o técnico mais próximo ---
                    client_lat, client_lon = get_lat_lon(zip_code)
                    if client_lat is not None and tech_data:
                        closest_tech = None
                        min_distance = float('inf')
                        
                        for tech in tech_data:
                            tech_zip = tech.get('zip_code')
                            if tech_zip:
                                tech_lat, tech_lon = get_lat_lon(tech_zip)
                                if tech_lat is not None:
                                    distance = calculate_distance(client_lat, client_lon, tech_lat, tech_lon)
                                    if distance < min_distance:
                                        min_distance = distance
                                        closest_tech = tech['nome']
                        
                        if closest_tech:
                            st.write(f"**Técnico mais próximo:** {closest_tech}")
                        else:
                            st.write("**Técnico mais próximo:** Não foi possível determinar (CEP(s) de origem ausente(s) ou inválido(s))")

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
        st.session_state.tech_data = saved_data if saved_data else [{"nome": "", "zip_code": "", "cidades": []}]
            
    st.info("Insira o nome do técnico, seu CEP de origem e as cidades onde ele realiza atendimentos. Você pode adicionar novas cidades digitando no campo e pressionando Enter.")

    header_cols = st.columns([0.3, 0.2, 0.4, 0.1])
    with header_cols[0]:
        st.markdown("**Nome do Técnico**")
    with header_cols[1]:
        st.markdown("**CEP de Origem**")
    with header_cols[2]:
        st.markdown("**Cidades de Atendimento**")
    with header_cols[3]:
        st.markdown("**Excluir**")

    for i, entry in enumerate(st.session_state.tech_data):
        cols = st.columns([0.3, 0.2, 0.4, 0.1])
        
        with cols[0]:
            entry["nome"] = st.text_input(
                "Nome", 
                value=entry.get("nome", ""), 
                key=f"tech_name_{i}", 
                label_visibility="collapsed"
            )
        
        with cols[1]:
            entry["zip_code"] = st.text_input(
                "Zip Code", 
                value=entry.get("zip_code", ""), 
                key=f"tech_zip_code_{i}", 
                max_chars=5,
                label_visibility="collapsed"
            )

        with cols[2]:
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
        
        with cols[3]:
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            if len(st.session_state.tech_data) > 1:
                if st.button("🗑️", key=f"delete_btn_{i}", on_click=delete_row, args=(i,)):
                    st.rerun()

    st.markdown("---")
    col_buttons = st.columns([0.25, 0.25, 0.5])
    with col_buttons[0]:
        if st.button("Adicionar nova linha"):
            add_new_row()
    with col_buttons[1]:
        if st.button("Salvar"):
            save_tech_data(st.session_state.tech_data)
            st.success("Dados salvos com sucesso!")

    # Seção de Itinerários de Atendimento
    st.markdown("---")
    st.subheader("Itinerários de Atendimento")

    # Carrega os dados mais recentes para garantir que o dropdown esteja atualizado
    tech_data_itinerario = load_tech_data()
    tech_names = [tech['nome'] for tech in tech_data_itinerario]

    # Inicializa clientes_data com uma linha por padrão
    if 'clientes_data' not in st.session_state or len(st.session_state.clientes_data) == 0:
        st.session_state.clientes_data = [{"nome": "", "zip_code": ""}]
    
    if tech_names:
        selected_tech = st.selectbox("Selecione um técnico:", options=tech_names)

        st.markdown("---")
        st.subheader("Cadastro de Clientes")

        def delete_cliente_row(index):
            if len(st.session_state.clientes_data) > 1:
                st.session_state.clientes_data.pop(index)

        def add_new_cliente():
            st.session_state.clientes_data.append({"nome": "", "zip_code": ""})

        # Cabeçalho da tabela de clientes
        header_cols_clientes = st.columns([0.45, 0.45, 0.1])
        with header_cols_clientes[0]:
            st.markdown("**Nome do Cliente**")
        with header_cols_clientes[1]:
            st.markdown("**Zip Code**")
        with header_cols_clientes[2]:
            st.markdown("**Excluir**")

        # Linhas da tabela de clientes
        for i, entry in enumerate(st.session_state.clientes_data):
            cols_clientes = st.columns([0.45, 0.45, 0.1])
            with cols_clientes[0]:
                st.session_state.clientes_data[i]["nome"] = st.text_input(
                    "Nome do Cliente",
                    value=st.session_state.clientes_data[i]["nome"],
                    key=f"cliente_name_{i}",
                    label_visibility="collapsed"
                )
            with cols_clientes[1]:
                st.session_state.clientes_data[i]["zip_code"] = st.text_input(
                    "Zip Code do Cliente",
                    value=st.session_state.clientes_data[i]["zip_code"],
                    key=f"cliente_zip_{i}",
                    max_chars=5,
                    label_visibility="collapsed"
                )
            with cols_clientes[2]:
                if i > 0: # Não permite excluir a primeira linha
                    if st.button("🗑️", key=f"delete_cliente_btn_{i}", on_click=delete_cliente_row, args=(i,)):
                        st.rerun()
        
        st.markdown("---")
        if st.button("Adicionar novo cliente", key="add_cliente_btn", on_click=add_new_cliente):
            st.rerun()

        # Otimização de Rota
        if st.button("Otimizar Itinerário", key="otimizar_btn"):
            if not google_maps_api_key:
                st.error("Por favor, insira sua chave da Google Maps API para otimizar o itinerário.")
            elif not st.session_state.clientes_data or all(c['zip_code'] == '' for c in st.session_state.clientes_data):
                st.warning("Adicione clientes para otimizar o itinerário.")
            else:
                st.subheader("Itinerário Otimizado")
                
                # Coordenadas do ponto de partida
                selected_tech_info = next((tech for tech in tech_data_itinerario if tech['nome'] == selected_tech), None)
                tech_zip = selected_tech_info['zip_code'] if selected_tech_info else None
                tech_lat, tech_lon = get_lat_lon(tech_zip)
                
                if tech_lat is None:
                    st.error("Não foi possível obter as coordenadas de origem do técnico.")
                    st.stop()
                
                current_lat, current_lon = tech_lat, tech_lon
                current_zip = tech_zip

                # Coordenadas dos clientes
                clientes_coords = []
                for cliente in st.session_state.clientes_data:
                    if cliente['zip_code']:
                        lat, lon = get_lat_lon(cliente['zip_code'])
                        if lat is not None and lon is not None:
                            clientes_coords.append({'nome': cliente['nome'], 'lat': lat, 'lon': lon, 'zip_code': cliente['zip_code']})

                if not clientes_coords:
                    st.warning("Não foi possível encontrar as localizações dos clientes.")
                    st.stop()
                
                # Lógica do caixeiro viajante
                itinerario_ordenado = []
                pontos_nao_visitados = clientes_coords[:]
                
                while pontos_nao_visitados:
                    closest_cliente = None
                    min_distance = float('inf')

                    for cliente in pontos_nao_visitados:
                        distance = calculate_distance(current_lat, current_lon, cliente['lat'], cliente['lon'])
                        if distance < min_distance:
                            min_distance = distance
                            closest_cliente = cliente
                    
                    itinerario_ordenado.append(closest_cliente)
                    current_lat, current_lon = closest_cliente['lat'], closest_cliente['lon']
                    current_zip = closest_cliente['zip_code']
                    pontos_nao_visitados.remove(closest_cliente)

                st.write("A melhor sequência de atendimento é:")

                # Lista de cores para os clientes
                client_colors = [
                    [255, 99, 71],  # Vermelho tomate
                    [60, 179, 113], # Verde médio
                    [30, 144, 255], # Azul do céu
                    [255, 215, 0],  # Dourado
                    [147, 112, 219],# Roxo médio
                    [255, 105, 180],# Rosa choque
                    [0, 206, 209],  # Azul turquesa
                    [255, 140, 0]   # Laranja escuro
                ]
                
                # Monta a rota no mapa
                map_lines = []
                all_points_for_map = []
                
                # Adiciona o ponto de partida do técnico
                all_points_for_map.append({'position': [tech_lon, tech_lat], 'name': selected_tech_info['nome'], 'color': [255, 0, 0]})
                
                current_origin_zip = tech_zip
                
                for i, cliente in enumerate(itinerario_ordenado):
                    color = client_colors[i % len(client_colors)]
                    
                    st.markdown(f"**{i+1}.** <span style='color:rgb({color[0]},{color[1]},{color[2]})'>**{cliente['nome']}**</span> (CEP: {cliente['zip_code']})", unsafe_allow_html=True)
                    
                    # Calcula distância e duração usando a API do Google
                    distance, duration, polyline_encoded = get_driving_directions(google_maps_api_key, current_origin_zip, cliente['zip_code'])
                    
                    if distance and duration:
                        st.markdown(f"**Tempo:** {duration} | **Distância:** {distance}")
                    
                    # Decodifica a polyline para obter as coordenadas do trajeto
                    if polyline_encoded:
                        path_coords = polyline.decode(polyline_encoded)
                        # O pydeck usa [longitude, latitude]
                        path_coords_pydeck = [[lon, lat] for lat, lon in path_coords]

                        map_lines.append({
                            'path': path_coords_pydeck,
                            'color': color + [255],  # Adiciona opacidade total
                            'stroke_width': 5
                        })
                    
                    # Adiciona o ponto do cliente no mapa
                    all_points_for_map.append({
                        'position': [cliente['lon'], cliente['lat']],
                        'name': cliente['nome'],
                        'color': color
                    })
                    
                    # Atualiza o ponto de origem para a próxima iteração
                    current_origin_zip = cliente['zip_code']

                # Exibe o mapa com todos os pontos e rotas
                if all_points_for_map:
                    # Calcula o centro médio para a visão inicial
                    center_lat = sum(p['position'][1] for p in all_points_for_map) / len(all_points_for_map)
                    center_lon = sum(p['position'][0] for p in all_points_for_map) / len(all_points_for_map)

                    view_state = pdk.ViewState(
                        latitude=center_lat,
                        longitude=center_lon,
                        zoom=10
                    )

                    # Camada para as linhas do trajeto
                    line_layer = pdk.Layer(
                        "PathLayer",
                        data=map_lines,
                        get_path='path',
                        get_color='color',
                        get_width='stroke_width'
                    )

                    # Camada para os pontos de partida e dos clientes
                    point_layer = pdk.Layer(
                        "ScatterplotLayer",
                        data=pd.DataFrame(all_points_for_map),
                        get_position='position',
                        get_fill_color='color',
                        get_radius=1000,
                        pickable=True,
                    )
                    
                    # Ferramenta para exibir nome ao passar o mouse
                    tooltip = {
                        "html": "<b>Nome:</b> {name}",
                        "style": {
                            "backgroundColor": "steelblue",
                            "color": "white"
                        }
                    }

                    st.markdown("---")
                    st.subheader("Mapa da Rota")
                    st.pydeck_chart(pdk.Deck(
                        initial_view_state=view_state,
                        layers=[point_layer, line_layer],
                        tooltip=tooltip
                    ))

    else:
        st.info("Nenhum técnico cadastrado para exibir o itinerário.")
