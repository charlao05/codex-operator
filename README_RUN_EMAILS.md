**Como rodar os envios Wave 1 (seguro e testável)**

Requisitos:
- Python 3.8+ (recomendado 3.10/3.11/3.12)
- Virtualenv ativado (opcional)

1) Preparar App Password (Gmail)
   - Gere uma App Password em: https://myaccount.google.com/apppasswords
   - NÃO cole a senha em conversas. Use variável de ambiente ou digite quando solicitado.

2) Rodar em modo simulação (DRY-RUN)
   - Testa o fluxo sem enviar emails reais.

PowerShell (defina cwd antes):
```powershell
cd C:\Users\Charles\Desktop\codex-operator
python .\send_wave1_emails.py --dry-run
```

3) Rodar envio real (requer App Password)
- Defina a variável apenas para a sessão atual (não grava em disco):
```powershell
$env:GMAIL_APP_PASSWORD = 'SUA_APP_PASSWORD_AQUI'
cd C:\Users\Charles\Desktop\codex-operator
python .\send_wave1_emails.py
```

O script grava `wave1_sending_results.json` com resultados reais, ou `wave1_sending_results_simulated.json` em dry-run.

4) Gerar variantes (opcional)
- Para gerar variantes locais (A/B) dos 5 templates:
```powershell
cd C:\Users\Charles\Desktop\codex-operator
python .\scripts\generate_wave1_variants.py
```
- Saída: `data/wave1_variants.json`

5) Vertex AI (opcional, avançado)
- Se você quiser usar Vertex AI para gerar as variações automaticamente, defina `GOOGLE_APPLICATION_CREDENTIALS`
  apontando para um service account JSON com permissões `Vertex AI` e instale `google-cloud-aiplatform`.
- Exemplo (PowerShell):
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = 'C:\Users\Charles\Desktop\codex-operator\config\sa-key.json'
.venv\Scripts\python -m pip install --upgrade google-cloud-aiplatform
# Em seguida, rodar script de Vertex AI (se implementado)
```

Segurança:
- Para produção, cada cliente deve usar suas próprias credenciais (pessoa física/jurídica).
- Rotacione App Passwords/API keys se já foram expostas.

Contato:
- Se quiser que eu execute o envio real agora, responda "APROVADO — EXECUTAR" após definir a variável `GMAIL_APP_PASSWORD` na sua sessão PowerShell, ou escolha envio interativo.
