import tempfile
import pytest
from pathlib import Path
from src.agents.nf_agent import prepare_invoice_steps, load_sales


def test_prepare_invoice_steps_complete():
    sale = {
        "client_name": "Test Client",
        "amount": 150.0,
        "description": "Serviço de consultoria",
        "date": "2025-11-17",
    }
    result = prepare_invoice_steps(sale)
    assert "steps" in result
    assert "explicacao" in result
    assert isinstance(result["steps"], list)
    assert isinstance(result["explicacao"], str)
    assert len(result["steps"]) >= 3


def test_prepare_invoice_steps_missing_fields():
    sale = {}
    result = prepare_invoice_steps(sale)
    assert "steps" in result
    assert "explicacao" in result
    assert "missing_fields" in result
    assert isinstance(result["missing_fields"], list)


def test_load_sales_file_not_found():
    missing = Path("nonexistent_file_for_testing_12345.json")
    assert load_sales(missing) is None


def test_load_sales_invalid_json():
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, encoding="utf-8"
    ) as f:
        f.write("{invalid json}")
        temp_path = f.name
    try:
        with pytest.raises(ValueError):
            load_sales(temp_path)
    finally:
        Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([str(Path(__file__))])
