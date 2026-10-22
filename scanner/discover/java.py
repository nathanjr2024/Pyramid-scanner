import fnmatch
from pathlib import Path

from scanner.core import ServiceReport, TestItem
from scanner.extract.java_names import extrair_metodos

_PASTAS_BUILD = {"target", "build", "out", ".gradle", "node_modules", ".mvn"}


def _bate_padrao(nome: str, padroes: list) -> bool:
    return any(fnmatch.fnmatch(nome, p) for p in padroes)


def _eh_pasta_build(caminho: Path) -> bool:
    return any(parte in _PASTAS_BUILD for parte in caminho.parts)


def _registrar_metodos(relatorio: ServiceReport, camada: str, arquivo: Path) -> None:
    """Extrai metodos @Test do arquivo e registra um TestItem por metodo."""
    metodos = extrair_metodos(arquivo)
    if metodos:
        for nome_metodo, descricao in metodos:
            if camada == "unitario":
                relatorio.unitario += 1
            else:
                relatorio.integracao += 1
            relatorio.testes.append(
                TestItem(camada, str(arquivo), metodo=nome_metodo, descricao=descricao)
            )
    else:
        # Fallback: sem metodos detectados, conta o arquivo como 1 teste
        if camada == "unitario":
            relatorio.unitario += 1
        else:
            relatorio.integracao += 1
        relatorio.testes.append(TestItem(camada, str(arquivo)))


def varrer_java(nome: str, caminho_repo: Path, config_class: dict) -> ServiceReport:
    """
    Fase 1/2: classifica por nome de arquivo (*Test.java, *IT.java).
    Fase 4: extrai um TestItem por metodo @Test com descricao via @DisplayName ou camelCase.
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
        # Integracao tem precedencia (*IT.java e mais especifico que *Test.java)
        if _bate_padrao(nome_arq, padroes_integ):
            _registrar_metodos(relatorio, "integracao", arquivo)
        elif _bate_padrao(nome_arq, padroes_unit):
            _registrar_metodos(relatorio, "unitario", arquivo)

    return relatorio
