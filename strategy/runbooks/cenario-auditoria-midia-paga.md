# 🔍 Runbook: Diagnóstico e Takeover de Mídia Paga

> **Modo**: Campanha (NEXUS-Sprint) | **Duração**: 3–5 semanas | **Agentes**: 6–9

---

## Cenário

A agência assume (takeover) ou revisa contas de **Google Ads** e **Meta Ads** de um cliente — novo ou da carteira — com sinais de desperdício: custo subindo, conversões que não batem com as vendas, praças misturadas, contas sem padrão de nomes. O objetivo é **diagnosticar → montar um plano de ação com dono e prazo → rodar um teste controlado de escala** antes de mexer em verba maior.

Este runbook serve tanto para a auditoria de proposta ([Fase 0](../playbooks/fase-0-prospeccao.md)) quanto para a auditoria de takeover no onboarding ([Fase 1](../playbooks/fase-1-onboarding.md)) e a otimização contínua ([Fase 6](../playbooks/fase-6-resultados.md)).

**Regra:** agentes de IA analisam e recomendam. Alteração de verba, pausa de campanha e mudança de estrutura só com decisão do Tráfego e aval do Account/cliente.

## Roster de agentes

### Núcleo
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Paid Media Auditor | Auditoria completa por checklist; relatório priorizado | Tráfego (Mídia Paga) |
| Tracking & Measurement Specialist | Diagnóstico de conversões, tags, GA4, CAPI e UTMs | Tráfego (Mídia Paga) |
| PPC Campaign Strategist | Estrutura de Google Ads, lances e distribuição de verba | Tráfego (Mídia Paga) |
| Paid Social Strategist | Estrutura de Meta Ads, públicos e praças | Tráfego (Mídia Paga) |

### Especialistas
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Search Query Analyst | Termos de busca, negativas e intenção | Tráfego (Mídia Paga) |
| Ad Creative Strategist | Diagnóstico de criativos, fadiga e plano de testes | Tráfego + D.A. / Designers |
| Programmatic & Display Buyer | Revisão de posicionamentos de display, se houver | Tráfego (Mídia Paga) |

### Apoio
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Account Strategist | Narrativa do diagnóstico e plano para o cliente | Account |
| Pipeline Analyst | Cruzamento de leads/vendas do cliente com dados de mídia | Account + Tráfego |

## Plano de execução

### Semana 1: acessos e diagnóstico

```
Dia 1: Preparação
├── Account → confirma escopo da auditoria e aprovadores de verba
├── Tráfego → solicita acesso de leitura (Google Ads, Meta Business Suite, GA4, GTM)
└── Registro do projeto no VJOB

Dia 2–5: Auditoria
├── Paid Media Auditor (apoia) → checklist por blocos
│   ├── Estrutura: campanhas, conjuntos/grupos, nomenclatura
│   ├── Orçamento vs. retorno: custo, conversões, custo por resultado por campanha
│   ├── Conversões/rastreamento: eventos primários, duplicidade, janela
│   ├── Termos de busca: desperdício, falta de negativas
│   └── Higiene de contas e praças: contas duplicadas, segmentação geográfica,
│       acessos de ex-fornecedores, forma de pagamento
├── Tracking & Measurement Specialist (apoia) → teste de cada evento de conversão
├── Search Query Analyst (apoia) → mapa de termos e lista de negativas
├── PPC Campaign Strategist / Paid Social Strategist (apoiam) → leitura de estrutura
└── Tráfego → valida cada achado na plataforma (nada entra no relatório sem conferência)
```

### Semana 2: plano de ação

```
Dia 6–7: Priorização
├── Tráfego → classifica achados por impacto × esforço
│   ├── Correção imediata (ex.: evento duplicado, praça errada)
│   ├── Reestruturação (ex.: separar marca / genérico, praças)
│   └── Teste (ex.: novo lance, novo público, novo criativo)
└── Ad Creative Strategist (apoia) → plano de testes de criativo

Dia 8–9: Plano de ação
├── Cada ação com: dono (papel), prazo (DD/MM/AAAA), métrica de sucesso
├── Account Strategist (apoia) → narrativa para o cliente
└── Account + Tráfego → apresentam ao cliente; aprovação escrita das mudanças e da verba
```

### Semana 3: correções

```
├── Tráfego → aplica correções imediatas (rastreamento e higiene primeiro)
├── Tracking & Measurement Specialist (apoia) → revalida conversões após ajuste
├── Search Query Analyst (apoia) → sobe negativas aprovadas
└── Registro de cada alteração: data, conta, o que mudou, quem aprovou
```

### Semanas 4–5: teste controlado de escala

```
Desenho do teste
├── Uma variável por vez (verba, lance, público ou criativo)
├── Grupo de controle mantido sem alteração
├── Aumento de verba em degraus (ex.: +20% por degrau — meta sugerida — validar)
├── Critério de parada definido antes de começar
└── Duração mínima para ler o resultado (meta sugerida — validar)

Execução e leitura
├── Tráfego → executa e acompanha diariamente
├── Paid Media Auditor (apoia) → leitura dos resultados contra o controle
├── Pipeline Analyst (apoia) → confere leads/vendas reportados pelo cliente
└── Account + Tráfego → decisão: escalar, manter ou reverter → registro no relatório (Gate G6)
```

## Quality gates

- [ ] Acessos de leitura concedidos antes do início da auditoria
- [ ] Todos os eventos de conversão testados e documentados
- [ ] Cada achado conferido por humano na plataforma
- [ ] Plano de ação com dono, prazo e métrica para cada item
- [ ] Mudanças de verba e estrutura aprovadas por escrito pelo cliente
- [ ] Log de alterações mantido (data, conta, mudança, aprovador)
- [ ] Teste de escala com controle e critério de parada definidos antes
- [ ] Relatório final sem dados pessoais de consumidores

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Conversões infladas levam a decisão errada | Corrigir rastreamento antes de qualquer teste de escala |
| Mudar tudo de uma vez e perder a leitura | Uma variável por teste; grupo de controle |
| Relatório genérico de IA | Achados validados na plataforma; Tráfego assina o relatório |
| Queda de desempenho no takeover | Não reestruturar na 1ª semana; começar por higiene e rastreamento |
| Acesso de terceiros ainda ativo | Revisar usuários e parceiros na higiene de contas |
| Praças misturadas distorcem resultado | Separar por praça quando o volume permitir |

## Métricas de sucesso (meta sugerida — validar)

| Métrica | Meta sugerida — validar |
|---------|-------------------------|
| Diagnóstico entregue | até 5 dias úteis após os acessos |
| Eventos de conversão validados | 100% dos definidos |
| Gasto em termos irrelevantes | redução de 30% após negativas |
| Custo por resultado no teste vs. controle | igual ou melhor com verba maior |
| Itens do plano de ação concluídos no prazo | ≥ 80% |

## Roster (slugs para runbooks.json)

```
Núcleo — activation: "sempre"
  paid-media-auditor
  paid-media-tracking-specialist
  paid-media-ppc-strategist
  paid-media-paid-social-strategist

Especialistas — activation: "semana 1+"
  paid-media-search-query-analyst
  paid-media-creative-strategist
  paid-media-programmatic-buyer

Apoio — activation: "sob demanda"
  sales-account-strategist
  sales-pipeline-analyst
```

---

*Método: Ciclo de Operação da Agência (CICLO). Handoffs: [../coordination/handoff-templates.md](../coordination/handoff-templates.md). Prompts: [../coordination/agent-activation-prompts.md](../coordination/agent-activation-prompts.md).*
