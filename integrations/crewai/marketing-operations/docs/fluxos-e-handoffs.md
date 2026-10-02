# Fluxos, Dependências e Handoffs

## 1. Sequência de tarefas e dependências (`context`)

| # | Tarefa | Agente | Depende de (`context`) | Portão |
|---|--------|--------|------------------------|--------|
| 1 | `pesquisa_mercado` | 03 Pesquisador | briefing | |
| 2 | `mapa_seo` | 04 SEO | 1 | |
| 3 | `brief_estrategico` | 02 Estrategista | 1, 2 | |
| 4 | `revisao_g1` | 11 Guardião | 3 | |
| 5 | `portao_g1` | 01 Gerente (+ humano) | 3, 4 | **G1 · pedido** |
| 6 | `aplicacao_g1` | 02 Estrategista | 3, 4, 5 | **G1 · decisão** (reemite o brief integral) |
| 7 | `producao_conteudo` | 05 Redator | 6, 2 | |
| 8 | `calendario_social` | 06 Social | 6, 7, 1 | |
| 9 | `fluxos_email` | 07 E-mail | 6, 7 | |
| 10 | `plano_midia_paga` | 08 Mídia | 6, 2, 1, 9 | |
| 11 | `direcao_arte` | 09 Arte | 6, 7, 8, 9, 10 | |
| 12 | `revisao_g2` | 11 Guardião | 7–11 | |
| 13 | `portao_g2` | 01 Gerente (+ humano) | 12, 7–11 | **G2 · pedido** |
| 14 | `aplicacao_g2` | 01 Gerente | 13, 12, 7–11 | **G2 · decisão** (ajustes obrigatórios por entrega) |
| 15 | `plano_medicao` | 10 Analista | 6, 8, 9, 10 | |
| 16 | `pacote_publicacao` | 12 Publicação | 14, 15, 11, 7–10 | |
| 17 | `revisao_g3` | 11 Guardião | 16, 15, 14 | |
| 18 | `portao_g3` | 01 Gerente (+ humano) | 16, 17, 10 | **G3 · pedido** |
| 19 | `aplicacao_g3` | 01 Gerente | 18, 16, 17, 10 | **G3 · decisão** (status, canais e orçamento autorizados) |
| 20 | `execucao_publicacao` | 12 Publicação | 19, 16 | |
| 21 | `sumario_executivo` | 01 Gerente | 6, 14, 19, 20, 15 | |
| 22 | `relatorio_performance` | 10 Analista | dados exportados (crew separada) | |

> No processo `sequential`, a ordem acima é a ordem de execução. No `hierarchical`, o gerente
> decide a ordem, mas as dependências de `context` continuam valendo.

## 2. Portões de aprovação humana

| Portão | O que aprova | Quem aprova (sugestão) | Evidências apresentadas | Decisões possíveis |
|--------|--------------|------------------------|-------------------------|--------------------|
| **G1 · Estratégia** | Objetivos, público, mensagens, mix e orçamento | Gestor(a) de marketing / cliente | Resumo de 10 linhas, parecer do Guardião, riscos | Aprovar · Aprovar com ajustes · Reprovar |
| **G2 · Criativos e planos** | Conteúdo, calendário, e-mails, plano de mídia, direção de arte | Gestor(a) de marketing + marca/jurídico se setor regulado | Quadro de pareceres, amostras por canal | Por entrega: Aprovar · Ajustar · Reprovar |
| **G3 · Publicação e investimento** | Cronograma, canais, orçamento a ativar, rastreamento | Dono(a) do orçamento | Cronograma, orçamento, parecer final, checklist de rastreamento | Autorizar (com restrições) · Não autorizar |

Implementação no CrewAI: cada portão tem **duas tarefas**. A de pedido (`portao_gN`, com `human_input: true`)
consolida o que o aprovador precisa decidir e é onde a execução pausa. A de decisão (`aplicacao_gN`) roda
depois da liberação, registra a decisão e emite o documento que as tarefas seguintes consomem. Nada a jusante
lê o pedido; todos leem a aplicação.
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

As tarefas 7, 8, 9 e 10 são independentes entre si após G1 (exceto 10 que lê 9 para públicos
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
   Contrato validado na plataforma (2026-10-02), que **difere da documentação oficial**:

   - O validador só conhece `executionId`, `taskId` e `humanFeedback` (camelCase) mais as três URLs de
     webhook. **`isApprove` não existe**: é aceito e ignorado, junto com qualquer campo desconhecido.
   - A decisão é carregada só pelo texto de `humanFeedback`. Um texto curto e inequívoco, como
     `"Aprovado."`, libera o portão e a execução avança. Qualquer texto com instruções, mesmo começando por
     "aprovado", é lido como pedido de refação: a plataforma reexecuta o portão com o feedback e pausa de novo
     no mesmo ponto. Texto vazio e campo omitido também refazem o portão.
   - Use sempre o `executionId` **original** (o da execução disparada no kickoff). Ids de continuações
     devolvem "NoneType não é subscritável" ou ficam silenciosos.
   - O `taskId` é o UUID enviado no webhook de aprovação, não o nome da tarefa, e muda a cada portão.
   - A API devolve um `kickoff_id` novo em qualquer chamada, até com ids falsos; só o evento seguinte no
     receptor confirma que a retomada valeu.
   - Para pedir ajuste, envie o feedback com instruções (refação); para aprovar, envie `"Aprovado."`.
   `is_approve: false` faz a tarefa ser refeita com o feedback como contexto; `true` segue para
   a próxima tarefa. Os webhooks precisam ser repetidos na retomada (não são herdados).
4. **Registro.** O receptor grava o evento (`tipo = human_input`) e a resposta fica no trace da
   plataforma; o Gerente consolida as decisões no sumário executivo.

Aprovadores sugeridos: G1 planejamento/atendimento, G2 criação e marca (jurídico quando setor
regulado), G3 dono(a) do orçamento.

## 8. Por que cada portão tem duas tarefas

A retomada da plataforma (`/resume`) reexecuta **apenas a tarefa pausada**. Com um portão único, uma
devolução com feedback refazia só o texto do portão e o documento corrigido não existia para as tarefas
seguintes (observado: o Gerente afirmou que o brief havia sido reformulado sem reapresentá-lo). Com a divisão:

| Etapa | Tarefa | Quem executa | O que sai |
|-------|--------|--------------|-----------|
| Pedido | `portao_gN` | Gerente | Pedido de aprovação; refeito a cada devolução, com o feedback transcrito literalmente |
| Decisão | `aplicacao_g1` | Estrategista (dono do brief) | Registro de decisão G1 + **brief integral revisado** |
| Decisão | `aplicacao_g2` | Gerente | Decisão por entrega, com ajustes obrigatórios em texto exato e tipo (pontual ou recriação); o `pacote_publicacao` aplica os pontuais |
| Decisão | `aplicacao_g3` | Gerente | Status (aprovado, com restrições, reprovado ou pendente), canais e orçamento autorizados; o `execucao_publicacao` só age dentro disso |

O texto das tarefas de aplicação recebe, em tempo de montagem, o **modo do portão**:

- `CREW_HUMAN_GATES=true`: a tarefa só roda depois que um humano liberou o portão, então trata a decisão como
  aprovada e aplica o feedback humano registrado no pedido e os ajustes obrigatórios do Guardião.
- `CREW_HUMAN_GATES=false`: a decisão é "PENDENTE DE APROVAÇÃO HUMANA"; só os ajustes obrigatórios do Guardião
  são aplicados, o documento sai marcado como "VERSÃO NÃO APROVADA POR HUMANO" e o `execucao_publicacao`
  responde "NÃO EXECUTADO".

Fluxo recomendado: para alterar o documento, **devolva** com o feedback em texto (o pedido é refeito com o
feedback transcrito no topo e a tarefa de aplicação o lê); depois, para liberar o portão, envie `"Aprovado."`.
Uma aprovação em texto curto não carrega instruções: elas devem ter sido dadas na devolução anterior.

Verificado em execução real (Hospital Santa Júlia): após a devolução, a tarefa `aplicacao_g1` reemitiu o brief
integral nas nove seções com o objetivo restaurado. Falhas observadas e tratadas nos prompts: o pedido do portão
reescrevia o parecer do Guardião; o registro do G3 autorizava canais cujas peças estavam bloqueadas no G2.


## Regras de qualidade adicionadas após o piloto Santa Júlia (G2/G3)

- `aplicacao_g2` agora tem duas partes: registro da decisão e **reemissão integral** de cada peça que recebeu ajuste
  (do Guardião ou do feedback humano). O pacote de publicação lê a versão reemitida.
- Regra global (todas as tarefas, exceto portões): é proibido inventar pacientes, depoimentos, nomes ou idades de
  personagens, números sem fonte e garantias de resultado; personas só como perfil.
- As revisões (G1, G2, G3) só emitem apontamento que cite o trecho literal da peça, e varrem depoimento, garantia,
  superlativo sem fonte, promessa clínica e número sem fonte.
- O calendário social cobre todas as semanas da campanha, com ao menos 3 posts por semana.


## Salvaguardas adicionadas após o piloto de 02/10 (G3)

- **Portões (G1/G2/G3):** guardrail em código rejeita o pedido se faltar seção obrigatória, se o resultado do Guardião
  mudar ou se menos de 70% das linhas do parecer forem copiadas. Prompt proíbe reconstruir feedback humano.
  Limite conhecido: o código não consegue provar que o histórico de feedbacks é só o que o humano escreveu; a fonte
  confiável das decisões humanas é o registro do portal (Supabase), não o texto do pedido.
- **`aplicacao_g2`:** guardrail rejeita saída que afirme que depoimento/testemunho é real, colhido com consentimento ou
  autorizado. Ajuste de veracidade só remove ou marca [VALIDAR]; peças reemitidas no formato integral.
- **`pacote_publicacao`:** plano de e-mail, plano de mídia, conceito criativo e conteúdo longo não viram post; só entram no
  cronograma posts do calendário liberado, envios de e-mail e o artigo no canal Site/Blog. Datas só do calendário.
- **`revisao_g2`:** varredura do plano de mídia: serviço fora do briefing, plataforma fora das informadas, projeção sem
  fonte, soma de mídia diferente do orçamento e superlativo reprovam a peça.
