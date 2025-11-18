#!/usr/bin/env python
"""Script para obter autorização OAuth do Gmail e salvar credenciais.

Executa um fluxo OAuth interativo:
1. Abre o navegador para você autorizar
2. Salva o token autorizado em um arquivo JSON
3. Configure o caminho no .env como GMAIL_CREDENTIALS_FILE

Execução:
python -m src.integrations.setup_gmail_oauth
"""
import os
import json
from pathlib import Path

def setup_gmail_oauth():
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
    except ImportError:
        print("[ERROR] Dependências OAuth não instaladas.")
        print("Execute: pip install google-auth-oauthlib")
        return False
    
    SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
    
    # Crie um arquivo credentials.json no Google Cloud Console (Desktop App)
    # Link: https://console.cloud.google.com/apis/credentials
    credentials_file = "credentials.json"  # Download do Google Cloud Console
    
    if not os.path.exists(credentials_file):
        print(f"[ERROR] Arquivo {credentials_file} não encontrado.")
        print("\nPassos para obter o arquivo:")
        print("1. Vá para https://console.cloud.google.com/apis/credentials")
        print("2. Clique 'Create Credentials' → 'OAuth 2.0 Client IDs'")
        print("3. Selecione 'Desktop application'")
        print("4. Clique 'Create' e depois 'Download JSON'")
        print("5. Renomeie para 'credentials.json' na raiz do projeto")
        print("6. Execute este script novamente\n")
        return False
    
    print("[Info] Iniciando fluxo OAuth do Gmail...")
    print("[Info] Um navegador será aberto pedindo autorização")
    print()
    
    try:
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_file, SCOPES
        )
        creds = flow.run_local_server(port=0)
        
        # Salvar credenciais autorizadas
        output_file = "gmail_authorized_user.json"
        with open(output_file, "w") as f:
            f.write(creds.to_json())
        
        print(f"\n[Success] Credenciais salvas em: {os.path.abspath(output_file)}")
        print(f"\nAdicione no seu .env:")
        print(f'GMAIL_CREDENTIALS_FILE="{os.path.abspath(output_file)}"')
        print(f'SENDER_EMAIL="charles.rsilva05@gmail.com"')
        print()
        return True
        
    except Exception as e:
        print(f"[ERROR] Falha ao configurar OAuth: {e}")
        return False

if __name__ == "__main__":
    success = setup_gmail_oauth()
    exit(0 if success else 1)
