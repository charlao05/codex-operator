from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from src.utils.logging_utils import get_logger
from src.utils.llm_client import gerar_texto_simples

logger = get_logger(__name__)


def load_finances(path: str | Path) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        logger.error("Arquivo de finanças não encontrado: %s", path)
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def summarize_finances(path: str | Path) -> Dict[str, Any]:
    data = load_finances(path)
    if not data:
        return {}

    total_revenue = sum(r.get("amount", 0) for r in data.get("revenues", []))
    total_expenses = sum(e.get("amount", 0) for e in data.get("expenses", []))
    profit = total_revenue - total_expenses

    summary = {
        "mei_id": data.get("mei_id"),
        "month": data.get("month"),
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "profit": profit,
    }

    # gerar texto explicativo via LLM
    prompt = (
        f"Gere um resumo financeiro em português simples para o MEI {data.get('mei_name')}\n"
        f"Mês: {data.get('month')}\n"
        f"Faturamento: R$ {total_revenue:.2f}, Despesas: R$ {total_expenses:.2f}, Lucro: R$ {profit:.2f}\n"
        "Explique em linguagem simples o que aconteceu e sugira 2 ações práticas para melhorar o lucro."
    )

    try:
        text = gerar_texto_simples(prompt)
    except Exception as e:
        logger.warning("LLM falhou: %s", e)
        text = (
            f"Resumo: Faturamento R$ {total_revenue:.2f}, Despesas R$ {total_expenses:.2f}, "
            f"Lucro R$ {profit:.2f}. Sugestão: revisar despesas e aumentar preço médio."
        )

    summary["texto"] = text
    return summary


if __name__ == "__main__":
    path = Path(__file__).resolve().parents[2] / "data" / "mei_finances_example.json"
    print(summarize_finances(path))
