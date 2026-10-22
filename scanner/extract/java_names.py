"""
Fase 4 - extracao de @DisplayName e nomes de metodo de arquivos Java.
Usa regex puro; sem dependencia de javalang.
"""
import re
from pathlib import Path
from typing import List, Optional, Tuple

_RE_DISPLAY_NAME = re.compile(r'@DisplayName\(\s*"([^"]+)"\s*\)')
_RE_TEST_ANNOTATION = re.compile(r'^\s*@Test\b')
_RE_METHOD_VOID = re.compile(r'\bvoid\s+(\w+)\s*\(')


def extrair_metodos(arquivo: Path) -> List[Tuple[str, str]]:
    """
    Retorna [(nome_metodo, descricao), ...] para cada metodo @Test encontrado.
    descricao = valor de @DisplayName se presente, senao camelCase split do nome.
    """
    try:
        texto = arquivo.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    linhas = texto.splitlines()
    resultados = []

    for i, linha in enumerate(linhas):
        if not _RE_TEST_ANNOTATION.match(linha):
            continue

        display_name = _buscar_display_name(linhas, i)

        # Assinatura do metodo nas proximas linhas apos @Test
        for j in range(i, min(i + 6, len(linhas))):
            m = _RE_METHOD_VOID.search(linhas[j])
            if m:
                nome_metodo = m.group(1)
                desc = display_name if display_name else camel_para_texto(nome_metodo)
                resultados.append((nome_metodo, desc))
                break

    return resultados


def _buscar_display_name(linhas: List[str], linha_test: int) -> Optional[str]:
    """
    Procura @DisplayName adjacente ao @Test.
    Busca primeiro nas linhas seguintes (padrao @Test > @DisplayName),
    depois nas anteriores (padrao @DisplayName > @Test).
    Nao ultrapassa 3 linhas em cada direcao para evitar pegar anotacoes da classe.
    """
    # Apos o @Test
    for j in range(linha_test + 1, min(linha_test + 4, len(linhas))):
        linha = linhas[j].strip()
        if not linha.startswith("@") and not linha == "":
            break  # chegou na assinatura do metodo
        m = _RE_DISPLAY_NAME.search(linha)
        if m:
            return m.group(1)

    # Antes do @Test (ex: @DisplayName\n@Test\nvoid)
    for j in range(linha_test - 1, max(-1, linha_test - 4), -1):
        linha = linhas[j].strip()
        if "class " in linha or linha.startswith("}"):
            break
        m = _RE_DISPLAY_NAME.search(linha)
        if m:
            return m.group(1)

    return None


def camel_para_texto(nome_metodo: str) -> str:
    """deveCopiarTodosOsCampos -> 'deve copiar todos os campos'"""
    palavras = re.sub(r"([A-Z])", r" \1", nome_metodo).strip()
    return palavras.lower()
