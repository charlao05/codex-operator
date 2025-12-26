from src.integrations.email_api import EmailAPI


class FakeSMTP:
    def __init__(self, host=None, port=None, timeout=None):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started = False
        self.logged_in = False
        self.sent = []

    def ehlo(self):
        return

    def starttls(self, context=None):
        self.started = True

    def login(self, user, password):
        self.logged_in = True

    def send_message(self, msg):
        self.sent.append(msg)

    def quit(self):
        return

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeSMTPSSL(FakeSMTP):
    pass


def test_send_email_monkeypatched(monkeypatch):
    # Configura variáveis de ambiente mínimas
    monkeypatch.setenv("EMAIL_SMTP_HOST", "smtp.test")
    monkeypatch.setenv("EMAIL_SMTP_PORT", "587")
    monkeypatch.setenv("SENDER_EMAIL", "noreply@test.local")

    # Substitui smtplib.SMTP e SMTP_SSL
    import smtplib

    monkeypatch.setattr(
        smtplib, "SMTP", lambda host, port, timeout=30: FakeSMTP(host, port, timeout)
    )
    monkeypatch.setattr(
        smtplib, "SMTP_SSL", lambda host, port, context=None: FakeSMTPSSL(host, port)
    )

    email_api = EmailAPI()
    res = email_api.send_email(
        ["cliente@test.local"], "Assunto teste", "Corpo da mensagem"
    )
    assert res["status"] == "sent"
