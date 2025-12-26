from datetime import datetime, timedelta, timezone

from src.integrations.google_calendar import GoogleCalendarAPI


class FakeEventsInsert:
    def __init__(self, payload):
        self.payload = payload

    def execute(self):
        return {"id": "evt123", "payload": self.payload}


class FakeEvents:
    def __init__(self):
        self.last_body = None

    def insert(self, calendarId=None, body=None):
        self.last_body = body
        return FakeEventsInsert(body)


class FakeService:
    def events(self):
        return FakeEvents()


def test_create_event_with_injected_service():
    gc = GoogleCalendarAPI(service_account_file=None, calendar_id="primary")
    start = datetime.now(timezone.utc) + timedelta(minutes=5)
    end = start + timedelta(minutes=30)
    svc = FakeService()
    res = gc.create_event(
        "Teste", start, end, attendees=["a@b.c"], description="desc", service=svc
    )
    assert res["status"] == "success"
    assert res["id"] == "evt123"


def test_create_event_from_sale_with_injected_service():
    sale = {
        "client_name": "João",
        "id": "sale-1",
        "client_email": "joao@ex.com",
        "amount": 100,
    }
    gc = GoogleCalendarAPI(service_account_file=None, calendar_id="primary")
    svc = FakeService()
    res = gc.create_event_from_sale(sale, service=svc)
    assert res["status"] == "success"
    assert res["id"] == "evt123"
