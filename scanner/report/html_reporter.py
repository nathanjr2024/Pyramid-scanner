import sys
from datetime import datetime
from pathlib import Path

from scanner.core import ServiceReport


def gerar_html(
    relatorios: list[ServiceReport],
    total: dict,
    destino: Path,
    template_dir: Path,
) -> None:
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except ImportError:
        sys.exit("Jinja2 nao instalado. Execute: pip install jinja2")

    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html"]),
    )
    template = env.get_template("report.html.j2")

    total_geral = sum(total.values())
    if total_geral:
        proporcoes = {
            "unitario":   round(total["unitario"]   / total_geral * 100, 1),
            "integracao": round(total["integracao"] / total_geral * 100, 1),
            "e2e":        round(total["e2e"]        / total_geral * 100, 1),
        }
    else:
        proporcoes = {"unitario": 0.0, "integracao": 0.0, "e2e": 0.0}

    repositorios = [
        {
            "nome":       r.nome,
            "unitario":   r.unitario,
            "integracao": r.integracao,
            "e2e":        r.e2e,
            "total":      r.total,
        }
        for r in relatorios
    ]

    html = template.render(
        total=total_geral,
        camadas=dict(total),
        proporcoes=proporcoes,
        repositorios=repositorios,
        gerado_em=datetime.now().strftime("%d/%m/%Y %H:%M"),
    )

    with open(destino, "w", encoding="utf-8") as f:
        f.write(html)
