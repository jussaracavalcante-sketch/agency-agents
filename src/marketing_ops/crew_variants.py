"""
crew_variants.py — variantes da crew principal (não usadas pelo deploy padrão).

  - MarketingOpsHierarchicalCrew: `Process.hierarchical`, o gerente delega livremente.
    Use após estabilizar o fluxo sequencial (README, fase F3).
  - PerformanceReportCrew: crew enxuta pós-campanha (só o Analista de Dados).
"""

from __future__ import annotations

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from .crew import MAX_RPM, MODEL, MarketingOpsCrew, analytics_tool, read_file


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
