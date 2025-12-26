import pytest
from pathlib import Path
from src.agents.collections_agent import (
    load_collections,
    find_overdue,
    generate_collection_message,
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def test_load_collections():
    data = load_collections(DATA_DIR / "mei_collections.json")
    assert isinstance(data, dict)
    assert data.get("mei_id") == "mei_001"


def test_find_overdue():
    overdue = find_overdue(DATA_DIR / "mei_collections.json")
    assert isinstance(overdue, list)
    assert len(overdue) >= 1
    assert overdue[0].get("status") == "overdue"


def test_generate_collection_message():
    invoice = {"client": "Test", "amount": 100.0, "due_date": "2025-11-01"}
    msg = generate_collection_message(invoice)
    assert isinstance(msg, str)
    assert len(msg) > 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__))])
