import pytest
from pathlib import Path
from src.agents.attendance_agent import (
    carregar_agenda,
    carregar_mensagens,
    sugerir_slots_basicos,
    processar_mensagens,
)

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"


def test_carregar_agenda():
    agenda = carregar_agenda(DATA_DIR / "mei_schedule.json")
    assert isinstance(agenda, dict)
    assert agenda.get("mei_name") == "Maria dos Santos"


def test_carregar_mensagens():
    msgs = carregar_mensagens(DATA_DIR / "mensagens_clientes.json")
    assert isinstance(msgs, list)
    assert len(msgs) >= 2
    assert msgs[0].texto.startswith("Oi, você tem horário")


def test_sugerir_slots_basicos():
    agenda = carregar_agenda(DATA_DIR / "mei_schedule.json")
    slots = sugerir_slots_basicos(agenda, quantidade=3)
    assert isinstance(slots, list)
    assert len(slots) == 3
    # formato YYYY-MM-DD HH:MM
    assert len(slots[0]) == 16


def test_processar_mensagens_demo():
    contexto = "Salão de estética e beleza"
    resultado = processar_mensagens(
        DATA_DIR / "mei_schedule.json", DATA_DIR / "mensagens_clientes.json", contexto
    )
    assert isinstance(resultado, list)
    assert len(resultado) >= 2
    for r in resultado:
        assert "resposta" in r
        assert "slots_sugeridos" in r
        assert isinstance(r["slots_sugeridos"], list)


if __name__ == "__main__":
    pytest.main([str(Path(__file__))])
