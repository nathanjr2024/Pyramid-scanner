import fnmatch
from pathlib import Path

from scanner.core import ServiceReport, TestItem

_PASTAS_BUILD = {"target", "build", "out", ".gradle", "node_modules", ".mvn"}

_PREFIXOS_CENARIO = (
    "Scenario:",
    "Scenario Outline:",
    "Cenario:",
    "Esquema do Cenario:",
)


def _bate_padrao(nome: str, padroes: list) -> bool:
    return any(fnmatch.fnmatch(nome, p) for p in padroes)


def _eh_pasta_build(caminho: Path) -> bool:
    return any(parte in _PASTAS_BUILD for parte in caminho.parts)


def varrer_e2e_cucumber(nome: str, caminho_repo: Path, config_class: dict) -> ServiceReport:
    """
    Conta cada Scenario / Scenario Outline de .feature como um teste E2E.
    Fase 4 (futuro): extrairá step definitions para o catálogo.
    """
    relatorio = ServiceReport(nome=nome, caminho_existe=caminho_repo.exists())

    if not caminho_repo.exists():
        return relatorio

    cfg_e2e     = config_class.get("e2e", {})
    padroes_e2e = cfg_e2e.get("padroes_arquivo", [])
    contar_cen  = cfg_e2e.get("contar_cenarios", True)

    for feature in sorted(caminho_repo.rglob("*.feature")):
        if _eh_pasta_build(feature):
            continue
        if not _bate_padrao(feature.name, padroes_e2e):
            continue

        if not contar_cen:
            relatorio.e2e += 1
            relatorio.testes.append(TestItem("e2e", str(feature), feature.stem))
            continue

        with open(feature, encoding="utf-8", errors="ignore") as f:
            for linha in f:
                stripped = linha.strip()
                for prefixo in _PREFIXOS_CENARIO:
                    if stripped.startswith(prefixo):
                        descricao = stripped[len(prefixo):].strip()
                        relatorio.e2e += 1
                        relatorio.testes.append(
                            TestItem("e2e", str(feature), descricao or feature.stem)
                        )
                        break

    return relatorio
