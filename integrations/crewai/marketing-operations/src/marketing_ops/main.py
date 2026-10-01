"""
main.py — ponto de entrada da Equipe de Operação de Marketing.

Uso:
  python -m marketing_ops.main                       # pipeline completo com briefing de exemplo
  python -m marketing_ops.main --briefing meu.yaml   # pipeline com briefing próprio
  python -m marketing_ops.main --hierarchical        # variante hierárquica
  python -m marketing_ops.main --report dados.csv --periodo "semana 1"   # relatório pós-campanha

O briefing segue docs/template-briefing.md (chaves = variáveis {…} de tasks.yaml).
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .crew import MarketingOpsCrew, MarketingOpsHierarchicalCrew, PerformanceReportCrew

load_dotenv()

BRIEFING_EXEMPLO = {
    "briefing_titulo": "Lançamento do programa de fidelidade",
    "cliente": "Loja Exemplo",
    "segmento": "Varejo de moda regional",
    "regiao": "Manaus e Região Metropolitana",
    "publico_alvo": "Mulheres 25-45, classes B/C, compram online e em loja física",
    "objetivo": "Gerar 2.000 adesões ao programa em 8 semanas",
    "orcamento_total": "R$ 60.000",
    "orcamento_midia": "R$ 35.000",
    "prazo": "8 semanas",
    "duracao_semanas": "8",
    "plataformas_sociais": "Instagram, TikTok, Facebook",
    "ferramenta_crm": "RD Station",
    "ferramenta_analytics": "GA4 + Google Tag Manager",
    "site_url": "https://www.exemplo.com.br",
    "fuso_horario": "America/Manaus",
}


def carregar_briefing(caminho: str | None) -> dict:
    if not caminho:
        return BRIEFING_EXEMPLO
    dados = yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))
    faltando = [k for k in BRIEFING_EXEMPLO if k not in dados]
    if faltando:
        sys.exit(f"Briefing incompleto. Faltam as chaves: {', '.join(faltando)}")
    return dados


def main() -> None:
    parser = argparse.ArgumentParser(description="Equipe de Operação de Marketing (CrewAI)")
    parser.add_argument("--briefing", help="arquivo YAML com o briefing (ver docs/template-briefing.md)")
    parser.add_argument("--hierarchical", action="store_true", help="usar processo hierárquico")
    parser.add_argument("--report", help="caminho de dados (CSV/JSON) para o relatório pós-campanha")
    parser.add_argument("--periodo", default="período completo", help="rótulo do período do relatório")
    args = parser.parse_args()

    Path("output").mkdir(exist_ok=True)
    inputs = carregar_briefing(args.briefing)

    if args.report:
        inputs.update({"caminho_dados": args.report, "periodo_relatorio": args.periodo})
        resultado = PerformanceReportCrew().crew().kickoff(inputs=inputs)
    elif args.hierarchical:
        resultado = MarketingOpsHierarchicalCrew().crew().kickoff(inputs=inputs)
    else:
        resultado = MarketingOpsCrew().crew().kickoff(inputs=inputs)

    print("\n" + "=" * 80)
    print(resultado)
    print("=" * 80)
    print("Artefatos salvos em ./output/")


if __name__ == "__main__":
    main()
