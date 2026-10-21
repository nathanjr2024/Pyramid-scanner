"""
Fase 5 — varredura de projetos TypeScript (BFF Jest / FED Karma + Jasmine).
Stub: retorna contagem por nome de arquivo; sem extração de describe/it ainda.
"""
import fnmatch
from pathlib import Path

from scanner.core import ServiceReport, TestItem

_PASTAS_BUILD = {"node_modules", "dist", "build", "out", ".angular"}


def _bate_padrao(nome: str, padroes: list) -> bool:
    return any(fnmatch.fnmatch(nome, p) for p in padroes)


def _eh_pasta_build(caminho: Path) -> bool:
    return any(parte in _PASTAS_BUILD for parte in caminho.parts)


def varrer_typescript(nome: str, caminho_repo: Path, config_class: dict) -> ServiceReport:
    """
    Fase 5 (stub): conta *.test.ts e *.spec.ts como unitários.
    Fase 5 completa: extrairá describe()/it() via regex para o catálogo.
    """
    relatorio = ServiceReport(nome=nome, caminho_existe=caminho_repo.exists())

    if not caminho_repo.exists():
        return relatorio

    padroes_unit = config_class.get("unitario", {}).get("padroes_arquivo", [])

    for arquivo in sorted(caminho_repo.rglob("*.ts")):
        if _eh_pasta_build(arquivo):
            continue
        if _bate_padrao(arquivo.name, padroes_unit):
            relatorio.unitario += 1
            relatorio.testes.append(TestItem("unitario", str(arquivo)))

    return relatorio
