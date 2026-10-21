#!/usr/bin/env python3
"""
Pyramid Scanner — entry point
================================
Dropar a pasta pyramid-scanner/ na raiz de qualquer workspace com
repositórios e executar a partir de lá.

Uso:
    python pyramid-scanner/run.py                        # tabela no terminal
    python pyramid-scanner/run.py --json                 # grava output/pyramid.json
    python pyramid-scanner/run.py --html                 # grava output/pyramid.html
    python pyramid-scanner/run.py --json --html          # ambos
    python pyramid-scanner/run.py --output-dir ./relat   # diretório personalizado
    python pyramid-scanner/run.py --config outro.yaml    # config alternativo
"""
import argparse
import sys
from pathlib import Path

# Raiz do workspace = pasta-pai de pyramid-scanner/
WORKSPACE_ROOT = Path(__file__).parent.parent

# Garante que os módulos de scanner sejam encontráveis como "scanner.*"
sys.path.insert(0, str(Path(__file__).parent))

from scanner.classify.rules import carregar_config, resolver_varredor
from scanner.core import ServiceReport
from scanner.report.html_reporter import gerar_html
from scanner.report.json_reporter import gerar_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Varredura da Piramide de Testes")
    parser.add_argument("--config",     default=None, help="Caminho para config.yaml")
    parser.add_argument("--json",       action="store_true", help="Grava output/pyramid.json")
    parser.add_argument("--html",       action="store_true", help="Grava output/pyramid.html")
    parser.add_argument("--output-dir", default=None, help="Diretorio de saida (padrao: pyramid-scanner/output/)")
    args = parser.parse_args()

    scanner_dir = Path(__file__).parent
    config_path = Path(args.config) if args.config else scanner_dir / "config.yaml"

    if not config_path.exists():
        sys.exit(f"Config nao encontrado: {config_path}")

    config     = carregar_config(config_path)
    output_dir = Path(args.output_dir) if args.output_dir else scanner_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    total: dict[str, int] = {"unitario": 0, "integracao": 0, "e2e": 0}
    relatorios: list[ServiceReport] = []

    for repo_cfg in config.get("repositorios", []):
        nome        = repo_cfg["nome"]
        tipo        = repo_cfg.get("tipo", "java")
        caminho     = (WORKSPACE_ROOT / repo_cfg["caminho"]).resolve()
        config_cl   = config.get("classificacao", {}).get(tipo, {})

        varrer = resolver_varredor(tipo)
        if varrer is None:
            print(f"[aviso] Tipo desconhecido '{tipo}' para '{nome}' -- pulando.", file=sys.stderr)
            relatorio = ServiceReport(nome=nome, caminho_existe=False)
        else:
            relatorio = varrer(nome, caminho, config_cl)

        total["unitario"]   += relatorio.unitario
        total["integracao"] += relatorio.integracao
        total["e2e"]        += relatorio.e2e
        relatorios.append(relatorio)

    _imprimir_tabela(relatorios, total)

    if args.json:
        destino = output_dir / "pyramid.json"
        gerar_json(relatorios, total, destino)
        print(f"JSON gravado em: {destino}")

    if args.html:
        template_dir = scanner_dir / "scanner" / "templates"
        destino      = output_dir / "pyramid.html"
        gerar_html(relatorios, total, destino, template_dir)
        print(f"HTML gravado em: {destino}")


def _imprimir_tabela(relatorios: list[ServiceReport], total: dict) -> None:
    total_geral = sum(total.values())
    largura     = max((len(r.nome) for r in relatorios), default=20)
    cab = f"{'Repositorio':<{largura}}  {'Unitario':>10}  {'Integracao':>10}  {'E2E':>8}  {'Total':>7}"
    sep = "-" * len(cab)

    print()
    print("=== Piramide de Testes ===")
    print()
    print(cab)
    print(sep)

    for r in relatorios:
        aviso = " [!] caminho nao encontrado" if not r.caminho_existe else ""
        print(f"{r.nome:<{largura}}  {r.unitario:>10}  {r.integracao:>10}  {r.e2e:>8}  {r.total:>7}{aviso}")

    print(sep)
    print(f"{'TOTAL':<{largura}}  {total['unitario']:>10}  {total['integracao']:>10}  {total['e2e']:>8}  {total_geral:>7}")

    if total_geral > 0:
        pct_u = total["unitario"]   / total_geral * 100
        pct_i = total["integracao"] / total_geral * 100
        pct_e = total["e2e"]        / total_geral * 100
        print()
        print("Proporcoes:")
        print(f"  Unitario   {pct_u:5.1f}%  {'#' * int(pct_u / 2)}")
        print(f"  Integracao {pct_i:5.1f}%  {'#' * int(pct_i / 2)}")
        print(f"  E2E        {pct_e:5.1f}%  {'#' * int(pct_e / 2)}")
    print()


if __name__ == "__main__":
    main()
