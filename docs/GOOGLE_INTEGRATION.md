# Integração Google Calendar

Resumo rápido:

- Método recomendado: use uma Service Account (JSON) com permissão para o Calendar API.
- Variáveis de ambiente usadas: `GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_CALENDAR_ID`.
- Módulo: `src.integrations.google_calendar.GoogleCalendarAPI`

Funcionalidades implementadas:

- `create_event(title, start, end, attendees=None, description=None)` — cria evento no calendário.
- `create_event_from_sale(sale)` — mapeia um registro de venda para um evento simples (título, horário curto, descrição).

Dependências:

- `google-api-python-client` e `google-auth` para uso do cliente real. Os testes podem injetar um `service` falso.

Como usar:

1. Crie Service Account no Google Cloud e baixe o JSON.
2. Defina `GOOGLE_SERVICE_ACCOUNT_FILE=/caminho/para/service-account.json` e `GOOGLE_CALENDAR_ID`.
3. No Python:

```py
from src.integrations.google_calendar import GoogleCalendarAPI
gc = GoogleCalendarAPI()
gc.create_event_from_sale(sale_record)
```
