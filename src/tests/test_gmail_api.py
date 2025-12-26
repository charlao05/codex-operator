from src.integrations.gmail_api import GmailAPI


class FakeMessagesSend:
    def __init__(self, body):
        self.body = body

    def execute(self):
        return {"id": "gmail123", "body": self.body}


class FakeMessages:
    def send(self, userId=None, body=None):
        return FakeMessagesSend(body)


class FakeUsers:
    def messages(self):
        return FakeMessages()


class FakeService:
    def users(self):
        return FakeUsers()


def test_send_message_injected_service():
    gmail = GmailAPI()
    svc = FakeService()
    res = gmail.send_message(
        ["a@b.c"], "Assunto", "Corpo", sender="noreply@test.local", service=svc
    )
    assert res["status"] == "sent"
    assert res["id"] == "gmail123"
