# 📣 Equipe de Operação de Marketing — CrewAI

> **Versão:** 1.0 · **Processo:** `hierarchical` (gerente delega) com sub-fluxos `sequential` · **Agentes:** 12 · **Portões humanos:** 3

---

## 1. Resumo Executivo

Esta documentação especifica uma **crew de operação de marketing** no CrewAI capaz de
executar, de ponta a ponta, o ciclo operacional de marketing de uma agência ou de um
departamento interno: receber um briefing, pesquisar mercado, planejar a campanha,
produzir conteúdo multicanal (orgânico, pago, e-mail), garantir conformidade de marca e
regulatória, publicar, medir e reportar.

A equipe foi desenhada com três princípios:

1. **Separação de responsabilidades** — cada agente tem um papel único, um objetivo
   mensurável e um conjunto restrito de ferramentas.
2. **Humano no circuito nas decisões irreversíveis** — três portões de aprovação
   (estratégia, criativos, publicação/investimento) impedem que a crew publique ou
   gaste sem validação.
3. **Rastreabilidade** — toda tarefa produz um artefato versionável (Markdown, JSON ou
   CSV) com fonte, premissas e indicador associado.

**Resultado esperado:** reduzir o ciclo briefing → campanha no ar de semanas para dias,
com qualidade auditável e indicadores padronizados.

---

## 2. Diagnóstico: por que uma crew e não um único agente

| Problema do agente único | Como a crew resolve |
|--------------------------|---------------------|
| Prompt gigante, contexto saturado, qualidade cai no meio da tarefa | Cada agente opera com contexto focado e recebe só o que precisa via `context` |
| Mistura de papéis (quem escreve também revisa) | Revisão independente pelo Guardião de Marca & Compliance |
| Sem ponto natural para aprovação humana | Tarefas com `human_input: true` nos portões |
| Métricas difusas | KPIs por agente e por tarefa (`expected_output` estruturado) |
| Difícil evoluir | Trocar/afinar um agente não afeta os demais |

---

## 3. Arquitetura da Crew

### 3.1 Organograma funcional

```
                         ┌──────────────────────────────────┐
                         │ 01 · Gerente de Operações de     │
                         │      Marketing (manager_agent)   │
                         └───────────────┬──────────────────┘
          ┌───────────────┬──────────────┼──────────────┬───────────────┐
          ▼               ▼              ▼              ▼               ▼
 ┌────────────────┐ ┌───────────┐ ┌─────────────┐ ┌───────────┐ ┌────────────────┐
 │ ESTRATÉGIA     │ │ CONTEÚDO  │ │ MÍDIA/CRM   │ │ CRIATIVO  │ │ QUALIDADE/DADOS│
 │ 02 Estrategista│ │ 05 Redator│ │ 07 E-mail   │ │ 09 Diretor│ │ 10 Analista    │
 │ 03 Pesquisador │ │ 06 Social │ │ 08 Mídia    │ │    de Arte│ │ 11 Guardião    │
 │ 04 SEO         │ │           │ │    Paga     │ │           │ │ 12 Publicação  │
 └────────────────┘ └───────────┘ └─────────────┘ └───────────┘ └────────────────┘
```

### 3.2 Roster

| # | Agente | Célula | Entrega principal | Ficha |
|---|--------|--------|-------------------|-------|
| 01 | Gerente de Operações de Marketing | Gestão | Plano de execução, delegação, consolidação | [agents/01](agents/01-gerente-operacoes-marketing.md) |
| 02 | Estrategista de Campanhas | Estratégia | Brief estratégico, objetivos, canais, orçamento | [agents/02](agents/02-estrategista-campanhas.md) |
| 03 | Pesquisador de Mercado & Tendências | Estratégia | Relatório de mercado, concorrência, tendências | [agents/03](agents/03-pesquisador-mercado-tendencias.md) |
| 04 | Especialista SEO | Estratégia | Mapa de palavras-chave, pautas, requisitos on-page | [agents/04](agents/04-especialista-seo.md) |
| 05 | Redator de Conteúdo | Conteúdo | Artigos, landing pages, roteiros | [agents/05](agents/05-redator-conteudo.md) |
| 06 | Estrategista de Social Media | Conteúdo | Calendário e copies por plataforma | [agents/06](agents/06-estrategista-social-media.md) |
| 07 | Especialista em E-mail & CRM | Mídia/CRM | Fluxos de automação, segmentação, e-mails | [agents/07](agents/07-especialista-email-crm.md) |
| 08 | Gestor de Mídia Paga | Mídia/CRM | Estrutura de campanhas, públicos, copies de anúncio, budget | [agents/08](agents/08-gestor-midia-paga.md) |
| 09 | Diretor de Arte & Briefing Criativo | Criativo | Briefings visuais, prompts de imagem, specs por formato | [agents/09](agents/09-diretor-arte-briefing-criativo.md) |
| 10 | Analista de Dados & Performance | Qualidade/Dados | Plano de medição, dashboards, relatórios | [agents/10](agents/10-analista-dados-performance.md) |
| 11 | Guardião de Marca & Compliance | Qualidade/Dados | Parecer de revisão (marca, LGPD, CONAR, plataformas) | [agents/11](agents/11-guardiao-marca-compliance.md) |
| 12 | Coordenador de Publicação & Distribuição | Qualidade/Dados | Pacote final, cronograma de publicação, checklist | [agents/12](agents/12-coordenador-publicacao-distribuicao.md) |

### 3.3 Fluxo macro (pipeline)

```
Briefing ──► [03 Pesquisa] ──► [04 SEO] ──► [02 Estratégia] ──► ⛔ G1 Aprovação da estratégia
                                                                   │
            ┌──────────────────────────────────────────────────────┘
            ▼
   [05 Redator] ─┐
   [06 Social]  ─┼──► [09 Direção de Arte] ──► [11 Revisão] ──► ⛔ G2 Aprovação dos criativos
   [07 E-mail]  ─┤
   [08 Mídia]   ─┘
                                                                   │
            ┌──────────────────────────────────────────────────────┘
            ▼
   [10 Plano de medição] ──► [12 Pacote de publicação] ──► ⛔ G3 Aprovação de publicação e investimento
                                                                   │
                                                                   ▼
                                              [10 Relatório de performance] ──► [01 Consolidação]
```

Detalhes de cada tarefa, dependências (`context`) e templates de handoff em
[`docs/fluxos-e-handoffs.md`](docs/fluxos-e-handoffs.md).

---

## 4. Matriz RACI

R = Responsável · A = Aprovador · C = Consultado · I = Informado

| Entrega | 01 Ger. | 02 Estr. | 03 Pesq. | 04 SEO | 05 Red. | 06 Social | 07 E-mail | 08 Mídia | 09 Arte | 10 Dados | 11 Guard. | 12 Publ. | Humano |
|---------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Relatório de mercado | A | C | **R** | C | I | I | I | C | I | C | I | I | I |
| Mapa de palavras-chave | A | C | C | **R** | C | I | I | C | I | I | I | I | I |
| Brief estratégico (G1) | C | **R** | C | C | I | I | I | C | I | C | C | I | **A** |
| Conteúdo longo | C | C | I | C | **R** | I | I | I | C | I | C | I | I |
| Calendário social | C | C | I | I | C | **R** | I | I | C | I | C | I | I |
| Fluxos de e-mail | C | C | I | I | C | I | **R** | I | C | C | C | I | I |
| Estrutura de mídia paga | C | C | C | C | I | I | I | **R** | C | C | C | I | I |
| Briefings criativos | C | I | I | I | C | C | C | C | **R** | I | C | I | I |
| Parecer de revisão (G2) | C | I | I | I | I | I | I | I | I | I | **R** | I | **A** |
| Plano de medição | C | C | I | I | I | I | C | C | I | **R** | I | C | I |
| Pacote de publicação (G3) | C | I | I | I | I | I | I | C | I | C | C | **R** | **A** |
| Relatório de performance | A | C | I | C | I | C | C | C | I | **R** | I | I | I |
| Consolidação executiva | **R** | C | I | I | I | I | I | I | I | C | I | I | I |

---

## 5. Indicadores (KPIs e OKRs)

### 5.1 KPIs operacionais da crew

| KPI | Definição | Meta inicial | Fonte |
|-----|-----------|--------------|-------|
| Lead time briefing → G1 | Horas entre entrada do briefing e brief estratégico aprovado | ≤ 8h úteis | Logs da crew |
| Lead time G1 → G3 | Horas entre estratégia aprovada e pacote pronto para publicar | ≤ 24h úteis | Logs da crew |
| Taxa de aprovação em 1ª rodada | % de entregas aprovadas sem retrabalho nos portões | ≥ 70% | Registro de portões |
| Taxa de reprovação por compliance | % de peças barradas pelo Guardião | ≤ 10% (tendência de queda) | Pareceres do agente 11 |
| Custo por execução | Tokens × preço do modelo por campanha | Baseline no mês 1, −20% no mês 3 | Telemetria LLM |
| Cobertura de rastreabilidade | % de entregas com fonte e premissas explícitas | 100% | Auditoria amostral |

### 5.2 KPIs de negócio (acompanhados pelo Analista de Dados)

| Canal | KPI primário | KPI secundário |
|-------|--------------|----------------|
| Orgânico / SEO | Sessões orgânicas, posições top 10 | CTR, tempo na página |
| Social | Alcance, taxa de engajamento | Salvamentos, cliques no perfil |
| E-mail | Taxa de clique (CTR), conversão | Descadastro, entregabilidade |
| Mídia paga | ROAS, CPA | CTR, Quality Score, frequência |
| Geral | Leads qualificados (MQL), CAC | Pipeline influenciado, receita atribuída |

### 5.3 OKRs sugeridos para o primeiro trimestre

- **O1 — Industrializar a produção de campanhas.**
  KR1: 100% das campanhas passam pelos 3 portões. KR2: lead time médio ≤ 32h úteis.
- **O2 — Elevar a qualidade e a conformidade.**
  KR1: zero incidentes de marca/compliance publicados. KR2: aprovação em 1ª rodada ≥ 70%.
- **O3 — Provar valor.**
  KR1: relatório de performance padronizado em 100% das campanhas. KR2: custo por campanha −20% vs. baseline.

---

## 6. Matriz de Riscos

| # | Risco | Prob. | Impacto | Mitigação | Dono |
|---|-------|:-----:|:-------:|-----------|------|
| R1 | Alucinação de dados de mercado ou benchmarks | Alta | Alto | Pesquisador obrigado a citar fonte/URL; Guardião valida; sem fonte = marcado `[VALIDAR]` | 03 / 11 |
| R2 | Publicação ou gasto sem aprovação | Baixa | Crítico | Ferramentas de escrita em plataformas só habilitadas após G3; `human_input: true` | 01 / 12 |
| R3 | Violação de LGPD em segmentação/e-mail | Média | Alto | Checklist LGPD obrigatório na revisão; sem dados pessoais nos prompts | 07 / 11 |
| R4 | Desvio de tom/identidade da marca | Média | Médio | Brand book como `knowledge`; revisão pelo Guardião | 11 |
| R5 | Estouro de custo de tokens (loops do gerente) | Média | Médio | `max_iter`, `max_rpm`, cache de ferramentas, modelo menor para tarefas simples | 01 / 10 |
| R6 | Dependência de APIs externas (Semrush, Ads) | Média | Médio | Fallback para pesquisa web + marcação de dados estimados | 03 / 08 |
| R7 | Conteúdo duplicado/plagiado | Baixa | Alto | Verificação de originalidade na revisão; prompts exigem síntese autoral | 05 / 11 |
| R8 | Falta de contexto do cliente (brief ruim) | Alta | Alto | Gerente valida completude do briefing antes de delegar; template obrigatório | 01 |

---

## 7. Plano de Implantação

### 7.1 Fases

| Fase | Objetivo | Entregas | Duração |
|------|----------|----------|---------|
| F0 · Preparação | Ambiente, chaves, brand book, briefing-padrão | `.env`, `knowledge/`, template de briefing | 1 semana |
| F1 · Núcleo | Rodar 02-03-04-05 em `sequential` com G1 | Brief + conteúdo longo validado | 1 semana |
| F2 · Multicanal | Adicionar 06-07-08-09 e revisão 11 com G2 | Pacote multicanal revisado | 2 semanas |
| F3 · Medição e publicação | Adicionar 10 e 12 com G3; gerente em `hierarchical` | Pipeline completo | 2 semanas |
| F4 · Integrações | Ferramentas reais (Semrush, Google Ads, Meta, CRM, GA4) | Tools customizadas e testes | 2–3 semanas |
| F5 · Operação assistida | Rodar com clientes reais, medir KPIs, ajustar prompts | Relatório de KPIs, backlog de melhorias | Contínuo |

### 7.2 Cronograma (10 semanas)

```
Semana:   1   2   3   4   5   6   7   8   9   10
F0       ███
F1           ███
F2               ███████
F3                       ███████
F4                               ███████████
F5                                       ███████ ▶
```

### 7.3 Plano de ação (5W2H resumido)

| O quê | Por quê | Quem | Quando | Onde | Como | Quanto |
|-------|---------|------|--------|------|------|--------|
| Configurar ambiente CrewAI | Base para tudo | Head de IA | Sem. 1 | Repositório | `requirements.txt`, `.env`, `crew.py` | Horas de setup |
| Carregar brand book e benchmarks | Reduz alucinação e desvio de marca | Marketing + IA | Sem. 1 | `knowledge/` | Markdown/PDF indexados | Baixo |
| Validar núcleo (F1) com 2 briefings reais | Provar qualidade antes de escalar | Head de IA + Planejamento | Sem. 2 | Crew | Rodar, revisar, ajustar prompts | Tokens |
| Expandir para multicanal (F2) | Cobrir a operação completa | Head de IA + Conteúdo + Mídia | Sem. 3–4 | Crew | Ativar agentes 06–09, 11 | Tokens |
| Integrar plataformas (F4) | Dados reais, menos retrabalho | Engenharia | Sem. 6–8 | `src/marketing_ops/tools` | Tools customizadas | Dev + APIs |
| Medir KPIs e revisar mensalmente | Governança e melhoria contínua | Head de IA | Mensal | Dashboard | Relatório do agente 10 + telemetria | Baixo |

---

## 8. Estrutura de arquivos

```
marketing-operations/
├── README.md                      ← este documento (visão executiva)
├── agents/                        ← fichas detalhadas dos 12 agentes
├── config/
│   ├── agents.yaml                ← definição CrewAI dos agentes (role/goal/backstory)
│   └── tasks.yaml                 ← definição CrewAI das tarefas (description/expected_output)
├── docs/
│   ├── fluxos-e-handoffs.md       ← sequência de tarefas, portões, templates de handoff
│   ├── ferramentas.md             ← ferramentas nativas e customizadas por agente
│   ├── governanca-qualidade.md    ← guardrails, LGPD/CONAR, memória, avaliação
│   └── template-briefing.md       ← briefing padrão de entrada da crew
├── src/marketing_ops/
│   ├── crew.py                    ← classe @CrewBase com agentes, tarefas e processo
│   ├── main.py                    ← ponto de entrada (kickoff)
│   └── tools/                     ← esqueleto de ferramentas customizadas
├── requirements.txt
└── .env.example
```

---

## 9. Conclusão e Próximos Passos

A crew documentada aqui cobre o ciclo completo de operação de marketing com
responsabilidades claras, portões de aprovação e indicadores. O caminho recomendado é
**começar pequeno (F1), provar qualidade e só então escalar** para multicanal e
integrações reais.

**Próximos passos imediatos:**

1. Preencher `.env` e carregar o brand book em `knowledge/`.
2. Rodar `python -m marketing_ops.main` com um briefing real usando o template.
3. Registrar os KPIs do primeiro ciclo como baseline.
4. Priorizar as integrações de ferramentas pelo impacto (SEO e mídia paga primeiro).
