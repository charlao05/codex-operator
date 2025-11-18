import pytest
from pathlib import Path
from src.agents.finance_agent import load_finances, summarize_finances

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def test_load_finances():
    data = load_finances(DATA_DIR / "mei_finances_example.json")
    assert isinstance(data, dict)
    assert data.get("mei_id") == "mei_001"
    assert data.get("month") == "2025-11"


def test_summarize_finances():
    summary = summarize_finances(DATA_DIR / "mei_finances_example.json")
    assert "total_revenue" in summary
    assert "total_expenses" in summary
    assert "profit" in summary
    assert summary["total_revenue"] >= 0
    assert summary["total_expenses"] >= 0


if __name__ == "__main__":
    pytest.main([str(Path(__file__))])
