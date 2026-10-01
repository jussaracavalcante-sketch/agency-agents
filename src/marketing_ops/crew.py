"""
crew.py — Equipe de Operação de Marketing (CrewAI)

Define os 12 agentes e as 18 tarefas do pipeline de campanha (a 19ª, relatório de
performance, roda em uma crew separada pós-campanha). Os textos de role/goal/backstory e
description/expected_output vivem em config/agents.yaml e config/tasks.yaml; este arquivo
só liga agentes, tarefas, ferramentas, dependências (context) e processo.

Processo: pipeline completo em `Process.sequential` com a ordem definida abaixo. O gerente
conduz os portões humanos (human_input=True) como tarefas explícitas.

Variantes (hierárquica e relatório pós-campanha) ficam em crew_variants.py para que a
plataforma CrewAI encontre uma única classe @CrewBase neste arquivo.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool

from marketing_ops.tools import (
    AnalyticsReadTool,
    BrandBookTool,
    CrmReadTool,
    PaidMediaReadTool,
    PublishTool,
    SeoKeywordTool,
)



def _modelo_padrao() -> tuple[str, str]:
    """Escolhe o provedor pela chave disponível quando MODEL não é informado."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic/claude-sonnet-5-5", "anthropic/claude-haiku-4-5-20251001"
    if os.getenv("OPENAI_API_KEY"):
        return "openai/gpt-4o", "openai/gpt-4o-mini"
    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        return "gemini/gemini-2.5-pro", "gemini/gemini-2.5-flash"
    return "openai/gpt-4o", "openai/gpt-4o-mini"


_PADRAO, _PADRAO_LEVE = _modelo_padrao()
MODEL = os.getenv("MODEL", _PADRAO)
OUTPUT_DIR = Path(os.getenv("CREW_OUTPUT_DIR", "output"))
# Log em arquivo é opcional: a plataforma CrewAI já guarda o trace de cada execução.
LOG_FILE = os.getenv("CREW_LOG_FILE", "")


def _resolver_output_dir() -> Path | None:
    """
    Devolve uma pasta GRAVÁVEL para os artefatos (output_file das tarefas e log).
    Tenta OUTPUT_DIR; se o diretório de trabalho for somente leitura (caso de alguns
    containers), cai para a pasta temporária do sistema. Nunca derruba a crew.
    """
    candidatos = [OUTPUT_DIR, Path(tempfile.gettempdir()) / "marketing_ops_output"]
    for pasta in candidatos:
        try:
            pasta.mkdir(parents=True, exist_ok=True)
            sonda = pasta / ".gravavel"
            sonda.touch()
            sonda.unlink()
            return pasta.resolve()
        except OSError:
            continue
    return None


def _cwd_gravavel() -> bool:
    try:
        sonda = Path.cwd() / ".gravavel_cwd"
        sonda.touch()
        sonda.unlink()
        return True
    except OSError:
        return False


def _garantir_output_dir() -> None:
    """
    Garante que exista uma pasta `output/` relativa ao diretório de trabalho, porque o
    runtime da plataforma pode gravar um log relativo (`output/crew_log.json`) por conta
    própria. Se o diretório de trabalho for somente leitura, muda para a pasta temporária,
    onde `output/` pode ser criada. Nunca lança erro.
    """
    try:
        if not _cwd_gravavel():
            os.chdir(tempfile.gettempdir())
        Path("output").mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
    _resolver_output_dir()


def _aplicar_pasta_de_saida(tasks: list[Task]) -> str | None:
    """
    Reescreve os output_file das tarefas para caminhos absolutos dentro da pasta gravável,
    aplica a política de portões humanos e devolve o caminho do log (ou None).
    """
    pasta = _resolver_output_dir()
    for t in tasks:
        if t.output_file:
            t.output_file = str(pasta / Path(t.output_file).name) if pasta else None
        if t.human_input and not HUMAN_GATES:
            t.human_input = False
            t.description += (
                "\n\nMODO SEM HUMANO NESTA EXECUÇÃO: não há aprovador disponível. Produza apenas o PEDIDO "
                "de aprovação com o campo Decisão = PENDENTE DE APROVAÇÃO HUMANA. É PROIBIDO inventar nome "
                "de aprovador, data de decisão, aprovação ou reprovação. Liste o que o humano precisa decidir "
                "e siga com as entregas como estão, marcando as pendências."
            )
    if LOG_FILE and pasta:
        return str(pasta / Path(LOG_FILE).name)
    return None


# Também na importação: cobre qualquer caminho de carga que não passe por crew().
_garantir_output_dir()


def _blindar_log_em_arquivo() -> None:
    """
    O runtime da plataforma CrewAI pode anexar um log relativo (ex.: output/crew_log.json)
    à crew depois de montada, e gravá-lo a partir de um diretório de trabalho que nós não
    controlamos. Um log que falha nunca deve derrubar uma campanha: antes de cada gravação,
    criamos a pasta do arquivo; se ainda assim falhar, registramos no stderr e seguimos.
    """
    try:
        from crewai.utilities import file_handler as fh
    except Exception:  # noqa: BLE001 - blindagem opcional
        return
    if getattr(fh.FileHandler, "_marketing_ops_blindado", False):
        return
    original_log = fh.FileHandler.log

    def log_resiliente(self, **kwargs):  # type: ignore[no-untyped-def]
        try:
            pasta = os.path.dirname(os.path.abspath(self._path))
            os.makedirs(pasta, exist_ok=True)
            return original_log(self, **kwargs)
        except Exception as exc:  # noqa: BLE001
            import sys

            print(f"[marketing_ops] log em arquivo ignorado: {exc}", file=sys.stderr)
            return None

    fh.FileHandler.log = log_resiliente  # type: ignore[method-assign]
    fh.FileHandler._marketing_ops_blindado = True  # type: ignore[attr-defined]


_blindar_log_em_arquivo()
MODEL_LIGHT = os.getenv("MODEL_LIGHT", MODEL if "MODEL" in os.environ else _PADRAO_LEVE)
MAX_RPM = int(os.getenv("CREW_MAX_RPM", "20"))
WRITE_TOOLS_ENABLED = os.getenv("CREW_ENABLE_WRITE_TOOLS", "false").lower() == "true"
# Portões humanos (G1/G2/G3) pausam a execução à espera de resposta. No terminal isso é um
# prompt; na plataforma CrewAI exige a configuração de Human-in-the-Loop (webhook). Sem
# essa configuração a execução trava ou é descartada, por isso o padrão aqui é desligado:
# os portões viram tarefas normais que produzem o pedido de aprovação como documento.
HUMAN_GATES = os.getenv("CREW_HUMAN_GATES", "false").lower() == "true"

# Ferramentas compartilhadas (instanciadas uma vez). Pesquisa web só com SERPER_API_KEY:
# sem a chave, os agentes trabalham com o briefing, o conhecimento carregado e o scraping
# de URLs informadas, marcando dados externos como [VALIDAR].
search = SerperDevTool() if os.getenv("SERPER_API_KEY") else None
scrape = ScrapeWebsiteTool()
read_file = FileReadTool()
seo_tool = SeoKeywordTool()
analytics_tool = AnalyticsReadTool()
brand_book = BrandBookTool()
crm_tool = CrmReadTool()
paid_media_tool = PaidMediaReadTool()
publish_tool = PublishTool(enabled=WRITE_TOOLS_ENABLED)


def _tools(*itens):
    """Lista de ferramentas sem as indisponíveis (None)."""
    return [t for t in itens if t is not None]


@CrewBase
class MarketingOpsCrew:
    """Pipeline sequencial completo: estratégia → produção → medição/publicação."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # ───────────────────────── Agentes ─────────────────────────

    @agent
    def gerente_operacoes(self) -> Agent:
        return Agent(config=self.agents_config["gerente_operacoes"], llm=MODEL, tools=[])

    @agent
    def estrategista_campanhas(self) -> Agent:
        return Agent(
            config=self.agents_config["estrategista_campanhas"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def pesquisador_mercado(self) -> Agent:
        return Agent(
            config=self.agents_config["pesquisador_mercado"],
            llm=MODEL,
            tools=_tools(brand_book, search, scrape, read_file, seo_tool),
        )

    @agent
    def especialista_seo(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_seo"],
            llm=MODEL,
            tools=_tools(search, scrape, read_file, seo_tool),
        )

    @agent
    def redator_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config["redator_conteudo"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def estrategista_social(self) -> Agent:
        return Agent(
            config=self.agents_config["estrategista_social"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def especialista_email_crm(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_email_crm"],
            llm=MODEL,
            tools=[brand_book, read_file, crm_tool],
        )

    @agent
    def gestor_midia_paga(self) -> Agent:
        return Agent(
            config=self.agents_config["gestor_midia_paga"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file, paid_media_tool),
        )

    @agent
    def diretor_arte(self) -> Agent:
        return Agent(config=self.agents_config["diretor_arte"], llm=MODEL, tools=[brand_book, read_file])

    @agent
    def analista_dados(self) -> Agent:
        return Agent(
            config=self.agents_config["analista_dados"],
            llm=MODEL,
            tools=[read_file, analytics_tool],
        )

    @agent
    def guardiao_marca_compliance(self) -> Agent:
        return Agent(
            config=self.agents_config["guardiao_marca_compliance"],
            llm=MODEL,
            tools=_tools(brand_book, search, read_file),
        )

    @agent
    def coordenador_publicacao(self) -> Agent:
        return Agent(
            config=self.agents_config["coordenador_publicacao"],
            llm=MODEL_LIGHT,
            tools=[read_file, publish_tool],
        )

    # ───────────────────────── Tarefas · Fase 1 ─────────────────────────

    @task
    def pesquisa_mercado(self) -> Task:
        return Task(config=self.tasks_config["pesquisa_mercado"])

    @task
    def mapa_seo(self) -> Task:
        return Task(config=self.tasks_config["mapa_seo"], context=[self.pesquisa_mercado()])

    @task
    def brief_estrategico(self) -> Task:
        return Task(
            config=self.tasks_config["brief_estrategico"],
            context=[self.pesquisa_mercado(), self.mapa_seo()],
        )

    @task
    def revisao_g1(self) -> Task:
        return Task(config=self.tasks_config["revisao_g1"], context=[self.brief_estrategico()])

    @task
    def portao_g1(self) -> Task:
        return Task(
            config=self.tasks_config["portao_g1"],
            context=[self.brief_estrategico(), self.revisao_g1()],
        )

    # ───────────────────────── Tarefas · Fase 2 ─────────────────────────

    @task
    def producao_conteudo(self) -> Task:
        return Task(
            config=self.tasks_config["producao_conteudo"],
            context=[self.portao_g1(), self.mapa_seo()],
        )

    @task
    def calendario_social(self) -> Task:
        return Task(
            config=self.tasks_config["calendario_social"],
            context=[self.portao_g1(), self.producao_conteudo(), self.pesquisa_mercado()],
        )

    @task
    def fluxos_email(self) -> Task:
        return Task(
            config=self.tasks_config["fluxos_email"],
            context=[self.portao_g1(), self.producao_conteudo()],
        )

    @task
    def plano_midia_paga(self) -> Task:
        return Task(
            config=self.tasks_config["plano_midia_paga"],
            context=[self.portao_g1(), self.mapa_seo(), self.pesquisa_mercado(), self.fluxos_email()],
        )

    @task
    def direcao_arte(self) -> Task:
        return Task(
            config=self.tasks_config["direcao_arte"],
            context=[
                self.portao_g1(),
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
            ],
        )

    @task
    def revisao_g2(self) -> Task:
        return Task(
            config=self.tasks_config["revisao_g2"],
            context=[
                self.producao_conteudo(),
                self.calendario_social(),
                self.fluxos_email(),
                self.plano_midia_paga(),
                self.direcao_arte(),
            ],
        )

    @task
    def portao_g2(self) -> Task:
        return Task(config=self.tasks_config["portao_g2"], context=[self.revisao_g2()])

    # ───────────────────────── Tarefas · Fase 3 ─────────────────────────

    @task
    def plano_medicao(self) -> Task:
        return Task(
            config=self.tasks_config["plano_medicao"],
            context=[self.portao_g1(), self.calendario_social(), self.fluxos_email(), self.plano_midia_paga()],
        )

    @task
    def pacote_publicacao(self) -> Task:
        return Task(
            config=self.tasks_config["pacote_publicacao"],
            context=[self.portao_g2(), self.plano_medicao(), self.direcao_arte()],
        )

    @task
    def revisao_g3(self) -> Task:
        return Task(
            config=self.tasks_config["revisao_g3"],
            context=[self.pacote_publicacao(), self.plano_medicao(), self.portao_g2()],
        )

    @task
    def portao_g3(self) -> Task:
        return Task(
            config=self.tasks_config["portao_g3"],
            context=[self.pacote_publicacao(), self.revisao_g3(), self.plano_midia_paga()],
        )

    @task
    def execucao_publicacao(self) -> Task:
        return Task(
            config=self.tasks_config["execucao_publicacao"],
            context=[self.portao_g3(), self.pacote_publicacao()],
        )

    @task
    def sumario_executivo(self) -> Task:
        return Task(
            config=self.tasks_config["sumario_executivo"],
            context=[
                self.portao_g1(),
                self.portao_g2(),
                self.portao_g3(),
                self.execucao_publicacao(),
                self.plano_medicao(),
            ],
        )

    # ───────────────────────── Crew ─────────────────────────

    @crew
    def crew(self) -> Crew:
        log_file = _aplicar_pasta_de_saida(self.tasks)
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,  # memória curta/longa entre tarefas (ver docs/governanca-qualidade.md)
            max_rpm=MAX_RPM,
            verbose=True,
            output_log_file=log_file,
        )
