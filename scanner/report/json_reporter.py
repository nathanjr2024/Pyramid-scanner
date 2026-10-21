import json
from pathlib import Path

from scanner.core import ServiceReport


def gerar_json(relatorios: list[ServiceReport], total: dict, destino: Path) -> None:
    total_geral = sum(total.values())
    proporcoes: dict[str, float] = {}
    if total_geral:
        proporcoes = {
            "unitario":   round(total["unitario"]   / total_geral * 100, 1),
            "integracao": round(total["integracao"] / total_geral * 100, 1),
            "e2e":        round(total["e2e"]        / total_geral * 100, 1),
        }

    dados = {
        "total": total_geral,
        "camadas": dict(total),
        "proporcoes": proporcoes,
        "repositorios": [
            {
                "nome":       r.nome,
                "unitario":   r.unitario,
                "integracao": r.integracao,
                "e2e":        r.e2e,
                "total":      r.total,
            }
            for r in relatorios
        ],
    }

    with open(destino, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
