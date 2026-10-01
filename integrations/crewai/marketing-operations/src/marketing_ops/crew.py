"""
crew.py — Equipe de Operação de Marketing (CrewAI)

Define os 12 agentes e as 18 tarefas do pipeline de campanha (a 19ª, relatório de
performance, roda em uma crew separada pós-campanha). Os textos de role/goal/backstory e
description/expected_output vivem em config/agents.yaml e config/tasks.yaml; este arquivo
só liga agentes, tarefas, ferramentas, dependências (context) e processo.

Processo:
  - MarketingOpsCrew: pipeline completo em `Process.sequential` com a ordem definida abaixo.
    O gerente conduz os portões humanos (human_input=True) como tarefas explícitas.
  - MarketingOpsHierarchicalCrew: variante `Process.hierarchical` em que o gerente delega
    livremente. Use após estabilizar o fluxo sequencial (ver README, fase F3).
"""

from __future__ import annotations

import os

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, ScrapeWebsiteTool, SerperDevTool

from .tools import (
    AnalyticsReadTool,
    CrmReadTool,
    PaidMediaReadTool,
    PublishTool,
    SeoKeywordTool,
)

MODEL = os.getenv("MODEL", "anthropic/claude-sonnet-5-5")
MODEL_LIGHT = os.getenv("MODEL_LIGHT", MODEL)
MAX_RPM = int(os.getenv("CREW_MAX_RPM", "20"))
WRITE_TOOLS_ENABLED = os.getenv("CREW_ENABLE_WRITE_TOOLS", "false").lower() == "true"

# Ferramentas compartilhadas (instanciadas uma vez)
search = SerperDevTool()
scrape = ScrapeWebsiteTool()
read_file = FileReadTool()
seo_tool = SeoKeywordTool()
analytics_tool = AnalyticsReadTool()
crm_tool = CrmReadTool()
paid_media_tool = PaidMediaReadTool()
publish_tool = PublishTool(enabled=WRITE_TOOLS_ENABLED)


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
            tools=[search, read_file],
        )

    @agent
    def pesquisador_mercado(self) -> Agent:
        return Agent(
            config=self.agents_config["pesquisador_mercado"],
            llm=MODEL,
            tools=[search, scrape, read_file, seo_tool],
        )

    @agent
    def especialista_seo(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_seo"],
            llm=MODEL,
            tools=[search, scrape, read_file, seo_tool],
        )

    @agent
    def redator_conteudo(self) -> Agent:
        return Agent(
            config=self.agents_config["redator_conteudo"],
            llm=MODEL,
            tools=[search, read_file],
        )

    @agent
    def estrategista_social(self) -> Agent:
        return Agent(
            config=self.agents_config["estrategista_social"],
            llm=MODEL,
            tools=[search, read_file],
        )

    @agent
    def especialista_email_crm(self) -> Agent:
        return Agent(
            config=self.agents_config["especialista_email_crm"],
            llm=MODEL,
            tools=[read_file, crm_tool],
        )

    @agent
    def gestor_midia_paga(self) -> Agent:
        return Agent(
            config=self.agents_config["gestor_midia_paga"],
            llm=MODEL,
            tools=[search, read_file, paid_media_tool],
        )

    @agent
    def diretor_arte(self) -> Agent:
        return Agent(config=self.agents_config["diretor_arte"], llm=MODEL, tools=[read_file])

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
            tools=[search, read_file],
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
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,  # memória curta/longa entre tarefas (ver docs/governanca-qualidade.md)
            max_rpm=MAX_RPM,
            verbose=True,
            output_log_file="output/crew_log.json",
        )


@CrewBase
class MarketingOpsHierarchicalCrew(MarketingOpsCrew):
    """
    Variante hierárquica: o gerente decide a ordem e delega. Mantém as mesmas tarefas e
    agentes; o gerente é passado como `manager_agent` e removido da lista de executores.
    """

    @crew
    def crew(self) -> Crew:
        manager = self.gerente_operacoes()
        workers = [a for a in self.agents if a.role.strip() != manager.role.strip()]
        return Crew(
            agents=workers,
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=manager,
            memory=True,
            max_rpm=MAX_RPM,
            verbose=True,
            output_log_file="output/crew_log.json",
        )


@CrewBase
class PerformanceReportCrew:
    """Crew enxuta pós-campanha: só o Analista de Dados e a tarefa de relatório."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def analista_dados(self) -> Agent:
        return Agent(
            config=self.agents_config["analista_dados"],
            llm=MODEL,
            tools=[read_file, analytics_tool],
        )

    @task
    def relatorio_performance(self) -> Task:
        return Task(config=self.tasks_config["relatorio_performance"])

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
