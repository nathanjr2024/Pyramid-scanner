from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TestItem:
    camada: str             # "unitario" | "integracao" | "e2e"
    arquivo: str
    metodo: Optional[str] = None
    descricao: Optional[str] = None


@dataclass
class ServiceReport:
    nome: str
    unitario: int = 0
    integracao: int = 0
    e2e: int = 0
    testes: list = field(default_factory=list)
    caminho_existe: bool = True

    @property
    def total(self) -> int:
        return self.unitario + self.integracao + self.e2e
