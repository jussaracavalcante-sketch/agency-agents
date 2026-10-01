"""
main.py — entrypoints da Equipe de Operação de Marketing (padrão CrewAI).

  crewai run                 → run()      pipeline completo com o briefing padrão
  crewai train -n 3 -f f.pkl → train()
  crewai replay -t <task_id> → replay()
  crewai test -n 2 -m <llm>  → test()

Linha de comando direta:
  python -m marketing_ops.main [--briefing meu.yaml] [--hierarchical]
  python -m marketing_ops.main --report dados.csv --periodo "semana 1"

O briefing segue docs/template-briefing.md (chaves = variáveis {…} de config/tasks.yaml).
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import yaml
from dotenv import load_dotenv

from marketing_ops.crew import MarketingOpsCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")
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


def carregar_briefing(caminho: str | None = None) -> dict:
    if not caminho:
        return dict(BRIEFING_EXEMPLO)
    dados = yaml.safe_load(Path(caminho).read_text(encoding="utf-8"))
    faltando = [k for k in BRIEFING_EXEMPLO if k not in dados]
    if faltando:
        sys.exit(f"Briefing incompleto. Faltam as chaves: {', '.join(faltando)}")
    return dados


def _preparar() -> dict:
    Path("output").mkdir(exist_ok=True)
    return carregar_briefing()


# ───────────── entrypoints padrão do CrewAI (pyproject [project.scripts]) ─────────────

def run():
    """Executa a crew com o briefing padrão (sobrescreva via inputs na plataforma)."""
    try:
        return MarketingOpsCrew().crew().kickoff(inputs=_preparar())
    except Exception as e:
        raise Exception(f"Erro ao executar a crew: {e}") from e


def train():
    """crewai train -n <iterações> -f <arquivo.pkl>"""
    try:
        MarketingOpsCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=_preparar()
        )
    except Exception as e:
        raise Exception(f"Erro ao treinar a crew: {e}") from e


def replay():
    """crewai replay -t <task_id>"""
    try:
        MarketingOpsCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Erro ao reexecutar a crew: {e}") from e


def test():
    """crewai test -n <iterações> -m <modelo avaliador>"""
    try:
        MarketingOpsCrew().crew().test(
            n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=_preparar()
        )
    except Exception as e:
        raise Exception(f"Erro ao testar a crew: {e}") from e


# ───────────── linha de comando direta ─────────────

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
        from marketing_ops.crew_variants import PerformanceReportCrew

        inputs.update({"caminho_dados": args.report, "periodo_relatorio": args.periodo})
        resultado = PerformanceReportCrew().crew().kickoff(inputs=inputs)
    elif args.hierarchical:
        from marketing_ops.crew_variants import MarketingOpsHierarchicalCrew

        resultado = MarketingOpsHierarchicalCrew().crew().kickoff(inputs=inputs)
    else:
        resultado = MarketingOpsCrew().crew().kickoff(inputs=inputs)

    print("\n" + "=" * 80)
    print(resultado)
    print("=" * 80)
    print("Artefatos salvos em ./output/")


if __name__ == "__main__":
    main()
