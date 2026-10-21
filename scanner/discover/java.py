import fnmatch
from pathlib import Path

from scanner.core import ServiceReport, TestItem

_PASTAS_BUILD = {"target", "build", "out", ".gradle", "node_modules", ".mvn"}


def _bate_padrao(nome: str, padroes: list) -> bool:
    return any(fnmatch.fnmatch(nome, p) for p in padroes)


def _eh_pasta_build(caminho: Path) -> bool:
    return any(parte in _PASTAS_BUILD for parte in caminho.parts)


def varrer_java(nome: str, caminho_repo: Path, config_class: dict) -> ServiceReport:
    """
    Fase 1/2: classifica por nome de arquivo (*Test.java, *IT.java).
    Fase 4 (futuro): refinará com leitura de anotações e @DisplayName.
    """
    relatorio = ServiceReport(nome=nome, caminho_existe=caminho_repo.exists())

    if not caminho_repo.exists():
        return relatorio

    padroes_unit  = config_class.get("unitario",  {}).get("padroes_arquivo", [])
    padroes_integ = config_class.get("integracao", {}).get("padroes_arquivo", [])

    for arquivo in sorted(caminho_repo.rglob("*.java")):
        if _eh_pasta_build(arquivo):
            continue
        nome_arq = arquivo.name
        # Integração tem precedência (*IT.java é mais específico que *Test.java)
        if _bate_padrao(nome_arq, padroes_integ):
            relatorio.integracao += 1
            relatorio.testes.append(TestItem("integracao", str(arquivo)))
        elif _bate_padrao(nome_arq, padroes_unit):
            relatorio.unitario += 1
            relatorio.testes.append(TestItem("unitario", str(arquivo)))

    return relatorio
