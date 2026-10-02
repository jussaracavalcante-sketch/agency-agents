"""
crew_variants.py — variantes da crew principal (não usadas pelo deploy padrão).

  - build_hierarchical_crew(): `Process.hierarchical`, o gerente delega livremente.
    Use após estabilizar o fluxo sequencial (README, fase F3).
  - build_report_crew(): crew enxuta pós-campanha (só o Analista de Dados).

A variante hierárquica é construída a partir da crew principal já montada em vez de herdar
de @CrewBase: no CrewAI 1.x, subclasses não herdam os agentes/tarefas decorados e a lista
`self.agents` só é preenchida dentro do método @crew.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from crewai import Agent, Crew, Process, Task

from marketing_ops.crew import (
    MAX_RPM,
    MEMORY_ENABLED,
    MODEL,
    MarketingOpsCrew,
    _aplicar_pasta_de_saida,
    _garantir_output_dir,
    _injetar_contexto_cliente,
    analytics_tool,
    read_file,
)


def build_hierarchical_crew() -> Crew:
    """Mesmos agentes e tarefas da crew principal, com o gerente como manager_agent."""
    main = MarketingOpsCrew().crew()  # agentes/tarefas só existem após .crew() no 1.x
    manager = next(a for a in main.agents if a.role.strip().startswith("Gerente"))
    workers = [a for a in main.agents if a is not manager]
    tasks = list(main.tasks)
    for t in tasks:  # tarefas do gerente ficam sem agente fixo: o manager as conduz
        if t.agent is manager:
            t.agent = None
    log_file = _aplicar_pasta_de_saida(tasks)
    return Crew(
        agents=workers,
        tasks=tasks,
        process=Process.hierarchical,
        manager_agent=manager,
        memory=MEMORY_ENABLED,
        max_rpm=MAX_RPM,
        verbose=True,
        output_log_file=log_file,
        before_kickoff_callbacks=[_injetar_contexto_cliente],
        chat_llm=MODEL,
    )


class MarketingOpsHierarchicalCrew:
    """Wrapper com a mesma interface `.crew()` usada em main.py."""

    def crew(self) -> Crew:
        return build_hierarchical_crew()


def _carregar_config(nome: str) -> dict:
    caminho = Path(__file__).parent / "config" / nome
    return yaml.safe_load(caminho.read_text(encoding="utf-8"))


def build_report_crew() -> Crew:
    """
    Só o Analista de Dados e a tarefa de relatório. Montada sem @CrewBase porque, no 1.x,
    o decorador exige que todos os agentes referenciados em tasks.yaml tenham método.
    """
    _garantir_output_dir()
    a_cfg = _carregar_config("agents.yaml")["analista_dados"]
    t_cfg = _carregar_config("tasks.yaml")["relatorio_performance"]
    analista = Agent(
        role=a_cfg["role"],
        goal=a_cfg["goal"],
        backstory=a_cfg["backstory"],
        allow_delegation=a_cfg.get("allow_delegation", False),
        verbose=a_cfg.get("verbose", True),
        max_iter=a_cfg.get("max_iter", 20),
        llm=MODEL,
        tools=[read_file, analytics_tool],
    )
    relatorio = Task(
        description=t_cfg["description"],
        expected_output=t_cfg["expected_output"],
        agent=analista,
        output_file=t_cfg.get("output_file"),
    )
    log_file = _aplicar_pasta_de_saida([relatorio])
    return Crew(
        agents=[analista],
        tasks=[relatorio],
        process=Process.sequential,
        verbose=True,
        output_log_file=log_file,
        chat_llm=MODEL,
    )


class PerformanceReportCrew:
    """Wrapper com a mesma interface `.crew()` usada em main.py."""

    def crew(self) -> Crew:
        return build_report_crew()
