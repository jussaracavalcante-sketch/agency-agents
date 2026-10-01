# 🤖 CrewAI Integration

Esta pasta contém a documentação e os artefatos de configuração para operar
agentes da Agency dentro do framework **[CrewAI](https://docs.crewai.com)**.

Diferente das demais integrações (geradas automaticamente pelo `scripts/convert.sh`),
o conteúdo aqui é **autoral e orientado a equipes (crews)**: em vez de converter
agentes individuais 1:1, documentamos times completos, com papéis, tarefas,
fluxos de handoff, portões de aprovação humana, indicadores e governança.

## Equipes disponíveis

| Equipe | Pasta | Agentes | Processo CrewAI | Status |
|--------|-------|---------|-----------------|--------|
| Operação de Marketing | [`marketing-operations/`](marketing-operations/README.md) | 12 | `hierarchical` (gerente) + sub-fluxos `sequential` | ✅ Documentado |

## Como o CrewAI organiza o trabalho

| Conceito CrewAI | O que é | Onde está documentado aqui |
|-----------------|---------|----------------------------|
| **Agent** | Papel com `role`, `goal`, `backstory`, ferramentas e limites | `marketing-operations/agents/*.md` + `config/agents.yaml` |
| **Task** | Unidade de trabalho com `description`, `expected_output`, `agent`, `context` | `marketing-operations/config/tasks.yaml` + `docs/fluxos-e-handoffs.md` |
| **Crew** | Conjunto de agentes + tarefas + processo (`sequential` / `hierarchical`) | `marketing-operations/src/marketing_ops/crew.py` |
| **Tools** | Funções/integrações que o agente pode acionar | `marketing-operations/docs/ferramentas.md` |
| **Memory / Knowledge** | Memória de curto e longo prazo, bases de conhecimento (brand book, benchmarks) | `marketing-operations/docs/governanca-qualidade.md` |
| **Human-in-the-loop** | `human_input: true` em tarefas que exigem aprovação | Portões G1–G3 em `docs/fluxos-e-handoffs.md` |

## Mapeamento Agency → CrewAI

Os agentes da Agency (`marketing/*.md`, `paid-media/*.md`, `design/*.md`, etc.)
são escritos como prompts de sistema ricos em identidade e processo. Para levá-los
ao CrewAI, aplicamos esta receita:

| Seção do agente Agency | Campo CrewAI |
|------------------------|--------------|
| `name` (frontmatter) | `role` |
| `description` + "Core Mission" | `goal` (1–3 frases, orientadas a resultado) |
| "Identity & Memory", "Personality", "Experience" | `backstory` |
| "Critical Rules You Must Follow" | `backstory` (seção de regras) + guardrails na `Task.description` |
| "Success Metrics" | KPIs documentados na ficha do agente e no `expected_output` |
| `tools` (frontmatter) | `tools=[...]` (SerperDevTool, ScrapeWebsiteTool, ferramentas customizadas) |

## Pré-requisitos

- Python 3.10–3.13
- `pip install crewai[tools] uv` (a CLI `crewai` usa `uv` para gerir dependências)
- Chave de um provedor LLM (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.)
- `SERPER_API_KEY` para pesquisa web (opcional, recomendado)

## Início rápido

```bash
cd integrations/crewai/marketing-operations
cp .env.example .env            # preencha as chaves
uv sync                         # ou: pip install -e .
crewai run                      # executa a crew com o briefing de exemplo
```

Veja o [README da equipe de Operação de Marketing](marketing-operations/README.md)
para a visão executiva, matriz RACI, KPIs, riscos e roadmap de implantação.
