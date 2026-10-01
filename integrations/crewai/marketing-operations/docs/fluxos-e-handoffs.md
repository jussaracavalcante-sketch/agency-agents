# Fluxos, Dependências e Handoffs

## 1. Sequência de tarefas e dependências (`context`)

| # | Tarefa | Agente | Depende de (`context`) | Portão |
|---|--------|--------|------------------------|--------|
| 1 | `pesquisa_mercado` | 03 Pesquisador | briefing | |
| 2 | `mapa_seo` | 04 SEO | 1 | |
| 3 | `brief_estrategico` | 02 Estrategista | 1, 2 | |
| 4 | `revisao_g1` | 11 Guardião | 3 | |
| 5 | `portao_g1` | 01 Gerente (+ humano) | 3, 4 | **G1** |
| 6 | `producao_conteudo` | 05 Redator | 5, 2 | |
| 7 | `calendario_social` | 06 Social | 5, 6, 1 | |
| 8 | `fluxos_email` | 07 E-mail | 5, 6 | |
| 9 | `plano_midia_paga` | 08 Mídia | 5, 2, 1, 8 | |
| 10 | `direcao_arte` | 09 Arte | 5, 6, 7, 8, 9 | |
| 11 | `revisao_g2` | 11 Guardião | 6–10 | |
| 12 | `portao_g2` | 01 Gerente (+ humano) | 11 | **G2** |
| 13 | `plano_medicao` | 10 Analista | 5, 7, 8, 9 | |
| 14 | `pacote_publicacao` | 12 Publicação | 12, 13, 10 | |
| 15 | `revisao_g3` | 11 Guardião | 14, 13, 12 | |
| 16 | `portao_g3` | 01 Gerente (+ humano) | 14, 15, 9 | **G3** |
| 17 | `execucao_publicacao` | 12 Publicação | 16, 14 | |
| 18 | `sumario_executivo` | 01 Gerente | 5, 12, 16, 17, 13 | |
| 19 | `relatorio_performance` | 10 Analista | dados exportados (crew separada) | |

> No processo `sequential`, a ordem acima é a ordem de execução. No `hierarchical`, o gerente
> decide a ordem, mas as dependências de `context` continuam valendo.

## 2. Portões de aprovação humana

| Portão | O que aprova | Quem aprova (sugestão) | Evidências apresentadas | Decisões possíveis |
|--------|--------------|------------------------|-------------------------|--------------------|
| **G1 · Estratégia** | Objetivos, público, mensagens, mix e orçamento | Gestor(a) de marketing / cliente | Resumo de 10 linhas, parecer do Guardião, riscos | Aprovar · Aprovar com ajustes · Reprovar |
| **G2 · Criativos e planos** | Conteúdo, calendário, e-mails, plano de mídia, direção de arte | Gestor(a) de marketing + marca/jurídico se setor regulado | Quadro de pareceres, amostras por canal | Por entrega: Aprovar · Ajustar · Reprovar |
| **G3 · Publicação e investimento** | Cronograma, canais, orçamento a ativar, rastreamento | Dono(a) do orçamento | Cronograma, orçamento, parecer final, checklist de rastreamento | Autorizar (com restrições) · Não autorizar |

Implementação no CrewAI: `human_input: true` nas tarefas `portao_g1`, `portao_g2`, `portao_g3`.
No terminal, o CrewAI pausa e pede a entrada do humano. Em produção, substitua por um
callback (`task_callback`) que envie o pedido a Slack/e-mail/Jira e aguarde a resposta.

## 3. Templates de handoff

### 3.1 Pedido de tarefa (Gerente → especialista)

```markdown
**Tarefa:** <nome>
**Contexto mínimo:** <cliente, campanha, objetivo, público, restrições>
**Insumos anexos:** <lista de artefatos>
**Entrega esperada:** <formato + seções obrigatórias>
**Critério de aceite:** <checklist>
**Prazo / limite de iterações:** <n>
```

### 3.2 Entrega (especialista → Gerente)

```markdown
**Entrega:** <nome do artefato>
**Resumo (3 bullets):**
**Premissas e fontes:**
**Itens [VALIDAR] / [AVAL ESPECIALISTA]:**
**Indicador associado:**
**Dependências para quem recebe:** <ex.: Diretor de Arte precisa de 6 peças 1080×1350>
```

### 3.3 Parecer (Guardião → autor + Gerente)

Ver template completo em [`../agents/11-guardiao-marca-compliance.md`](../agents/11-guardiao-marca-compliance.md).

### 3.4 Pedido de aprovação (Gerente → humano)

```markdown
**Portão:** G1 | G2 | G3
**Campanha:** <nome>
**O que está sendo aprovado:** <1 frase>
**Resumo:** <≤ 10 linhas>
**Parecer do Guardião:** Aprovado | Aprovado com ajustes (n) | Reprovado
**Riscos principais:** <3 bullets>
**Decisão solicitada:** Aprovar / Aprovar com ajustes / Reprovar
```

## 4. Marcadores padronizados

| Marcador | Significado | Quem resolve |
|----------|-------------|--------------|
| `[VALIDAR]` | Informação não confirmada por fonte | Autor ou humano antes do próximo portão |
| `[AVAL ESPECIALISTA]` | Claim de saúde, financeiro ou jurídico | Especialista humano (médico, jurídico, compliance) |
| `[DADO ESTIMADO]` | Número derivado de heurística/benchmark | Declarar método; Analista confirma pós-publicação |
| `[BLOQUEADO]` | Ação recusada por falta de aprovação | Gerente / humano |

## 5. Tempos-alvo por fase (SLA interno)

| Fase | Tarefas | Tempo-alvo de máquina | Tempo-alvo com humano |
|------|---------|-----------------------|-----------------------|
| 1 · Estratégia | 1–5 | ≤ 1h | ≤ 8h úteis (G1) |
| 2 · Produção | 6–12 | ≤ 2h | ≤ 16h úteis (G2) |
| 3 · Medição e publicação | 13–18 | ≤ 1h | ≤ 8h úteis (G3) |

## 6. Paralelização (opcional)

As tarefas 6, 7, 8 e 9 são independentes entre si após G1 (exceto 9 que lê 8 para públicos
de CRM). Em CrewAI, marque-as com `async_execution: true` e deixe `direcao_arte` aguardar
todas via `context`. Ganho esperado: 30–40% no tempo da fase 2.

## 7. Portões humanos na plataforma CrewAI (Human-in-the-Loop)

Os portões G1, G2 e G3 só pausam a execução quando `CREW_HUMAN_GATES=true` está nas
variáveis de ambiente da automação. Com a flag desligada (padrão), eles produzem um pedido
com "PENDENTE DE APROVAÇÃO HUMANA" e a execução segue até o fim.

Com a flag ligada, o fluxo é:

1. **Kickoff com webhook de aprovação.** Além de `taskWebhookUrl` e `crewWebhookUrl`, o corpo
   do kickoff leva `humanInputWebhook` com a URL do receptor e autenticação bearer:
   ```json
   "humanInputWebhook": {"url": "<receptor>?tipo=human_input", "authentication": {"strategy": "bearer", "token": "<segredo>"}}
   ```
2. **Pausa no portão.** A execução fica em "Awaiting Input" na aba Executions e aparece em
   "Human in the Loop". A plataforma envia ao receptor um evento com `execution_id`, `task_id`
   e a saída da tarefa (o pedido de aprovação do Gerente).
3. **Decisão.** O aprovador decide pela aba Human in the Loop **ou** por quem opera a API,
   chamando o endpoint de retomada da automação:
   ```json
   POST <API_URL>/resume
   {"executionId": "<kickoff_id>", "taskId": "<task_id recebido no webhook>",
    "humanFeedback": "Aprovado. Ajustar X.", "isApprove": true,
    "taskWebhookUrl": "...", "crewWebhookUrl": "...", "humanInputWebhook": {...}}
   ```
   Os campos são **camelCase** (a API rejeita `execution_id`). O `taskId` é o UUID enviado no
   webhook de aprovação, não o nome da tarefa. A resposta traz um novo `kickoff_id` para
   acompanhar a continuação. Validado em 2026-10-01 com a execução e73d4895 → bff9e967.
   `is_approve: false` faz a tarefa ser refeita com o feedback como contexto; `true` segue para
   a próxima tarefa. Os webhooks precisam ser repetidos na retomada (não são herdados).
4. **Registro.** O receptor grava o evento (`tipo = human_input`) e a resposta fica no trace da
   plataforma; o Gerente consolida as decisões no sumário executivo.

Aprovadores sugeridos: G1 planejamento/atendimento, G2 criação e marca (jurídico quando setor
regulado), G3 dono(a) do orçamento.
