from pathlib import Path
from typing import Callable, Optional

import yaml

from scanner.core import ServiceReport
from scanner.discover.e2e_cucumber import varrer_e2e_cucumber
from scanner.discover.java import varrer_java
from scanner.discover.typescript import varrer_typescript

_VARREDORES: dict[str, Callable] = {
    "java":         varrer_java,
    "e2e_cucumber": varrer_e2e_cucumber,
    "typescript":   varrer_typescript,
}


def carregar_config(caminho: Path) -> dict:
    with open(caminho, encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolver_varredor(tipo: str) -> Optional[Callable]:
    return _VARREDORES.get(tipo)
