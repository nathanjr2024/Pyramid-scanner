"""
Fase 4 — extração de @DisplayName do código Java via javalang.
Stub: retorna None; o catálogo usará camelCase split no nome do método.
"""
from pathlib import Path
from typing import Optional


def extrair_display_name(arquivo: Path) -> Optional[str]:
    # TODO Fase 4: usar javalang para extrair @DisplayName("…")
    # Fallback: converter camelCase → texto separado por espaço
    return None


def camel_para_texto(nome_metodo: str) -> str:
    """shouldReturnBeneficiario → 'should return beneficiario'"""
    import re
    palavras = re.sub(r"([A-Z])", r" \1", nome_metodo).strip()
    return palavras.lower()
