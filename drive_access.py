import os
import io
import streamlit as st
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# Se modificar os SCOPES, exclua o arquivo token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_drive_service():
    """
    Cria e retorna um objeto de serviço da API do Google Drive usando credenciais
    de uma conta de serviço.
    
    A conta de serviço deve ter permissão para visualizar os ficheiros e pastas.
    """
    # Obtém o caminho da pasta raiz do projeto de forma absoluta e segura.
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    credentials_path = os.path.join(script_dir, 'service_account.json')

    try:
        if not os.path.exists(credentials_path):
            st.error("Ficheiro 'service_account.json' não encontrado. Por favor, siga as instruções para criar e colocar o ficheiro no diretório raiz do projeto.")
            return None

        # Carrega as credenciais da conta de serviço a partir do ficheiro JSON.
        creds = service_account.Credentials.from_service_account_file(
            credentials_path,
            scopes=SCOPES
        )
        
        # Constrói e retorna o serviço da API do Drive.
        return build('drive', 'v3', credentials=creds)

    except Exception as e:
        st.error(f"Erro ao carregar credenciais da conta de serviço: {e}")
        return None

@st.cache_data(show_spinner=False)
def get_files_from_drive_folder(folder_id):
    """
    Procura recursivamente por arquivos Google Sheets e .xlsx numa pasta e suas subpastas.
    
    Parâmetros:
    - folder_id (str): O ID da pasta do Google Drive a ser procurada.

    Retorna:
    - list: Uma lista de objetos BytesIO, cada um contendo o conteúdo de uma planilha.
    """
    drive_service = get_drive_service()
    if not drive_service:
        return []
    
    try:
        file_contents = []
        
        # Consulta a API para encontrar todas as pastas dentro da pasta atual
        query = f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folders_response = drive_service.files().list(q=query, fields="files(id, name)").execute()

        # Chama recursivamente a função para cada subpasta encontrada
        for folder in folders_response.get('files', []):
            sub_folder_files = get_files_from_drive_folder(folder['id'])
            file_contents.extend(sub_folder_files)
        
        # Consulta a API para encontrar arquivos Google Sheets e .xlsx na pasta atual
        query = f"'{folder_id}' in parents and (mimeType='application/vnd.google-apps.spreadsheet' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet') and trashed=false"
        results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()

        # Baixa o conteúdo de cada arquivo de planilha encontrado
        for item in results.get('files', []):
            file_id = item['id']
            file_name = item['name']
            mime_type = item['mimeType']

            file_bytes = io.BytesIO()
            if mime_type == 'application/vnd.google-apps.spreadsheet':
                # Exporta o Google Sheet como um arquivo .xlsx
                request = drive_service.files().export_media(fileId=file_id, mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                file_name += '.xlsx'
            else:
                # Baixa o arquivo .xlsx diretamente
                request = drive_service.files().get_media(fileId=file_id)

            downloader = MediaIoBaseDownload(file_bytes, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()

            file_bytes.seek(0)
            file_contents.append(file_bytes)
            st.success(f"Planilha '{file_name}' processada.")

        return file_contents
    
    except HttpError as e:
        if e.resp.status == 404:
            st.error("ID da pasta não encontrado ou inválido. Por favor, verifique o ID e as permissões de acesso da conta de serviço.")
        else:
            st.error(f"Ocorreu um erro ao aceder à API do Google Drive: {e}")
        return []
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
        return []
