# Integração Email (SMTP)

Resumo rápido:

- Implementado cliente simples SMTP em `src.integrations.email_api.EmailAPI`.
- Variáveis de ambiente: `EMAIL_SMTP_HOST`, `EMAIL_SMTP_PORT`, `EMAIL_SMTP_USER`, `EMAIL_SMTP_PASSWORD`, `SENDER_EMAIL`.

Uso básico:

```py
from src.integrations.email_api import EmailAPI
api = EmailAPI()
api.send_email(["cliente@ex.com"], "Assunto", "Corpo da mensagem")
```

Observações:

- Suporta SSL (porta 465) e STARTTLS (porta 587).
- Anexos podem ser passados como caminhos de arquivo (serão lidos em modo binário).
- Para ambientes como Gmail, considere usar App Passwords ou OAuth na próxima iteração.
