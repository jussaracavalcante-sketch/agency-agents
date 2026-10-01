# ✅ Playbook Fase 4 — Aprovação e Controle de Qualidade

> **Modo**: Conta completa · Campanha · Demanda pontual | **Duração**: contínua no mês (por peça: 1–3 dias úteis — meta sugerida — validar) | **Agentes**: Brand Guardian, Ad Creative Strategist
>
> **Dono humano**: Analista de Social Media + Supervisão de Social Media | **Quem aprova**: Cliente (aprovador autorizado) | **Gate**: G4

---

## Objetivo

Garantir que **nenhuma peça seja publicada sem aprovação escrita e registrada** do Cliente, com qualidade interna conferida antes do envio. Esta fase ataca a dor número um da operação: **atrasos por dependência de aprovação** e **feedback fragmentado em vários canais**.

Princípios:

- Aprovação é **sempre por escrito** e fica **registrada** no card da peça (VJOB/iClips). Aprovação verbal ou por áudio não vale.
- Só aprova quem foi definido como **aprovador autorizado** no onboarding (Fase 1).
- Todo feedback de uma peça é consolidado em **um único registro por card**.
- A IA revisa e sinaliza. **Quem decide é humano.**

## Pré-requisitos (entrada)

- [ ] Gate G3 aprovado: peça revisada internamente com checklist da [Fase 3](fase-3-producao.md)
- [ ] Card da peça no VJOB/iClips com briefing, legenda, arte/vídeo final e data de publicação
- [ ] Lista de aprovadores autorizados do Cliente registrada no onboarding ([Fase 1](fase-1-onboarding.md))
- [ ] Canal oficial de aprovação definido (hoje WhatsApp; recomendado: e-mail ou registro rastreável, conforme POP)
- [ ] Janela de retorno acordada com o Cliente (meta sugerida — validar)

## Papéis humanos (RACI resumida)

| Atividade | Analista de Social | Supervisão | Account | Cliente | D.A./Criação | Tráfego |
|---|---|---|---|---|---|---|
| Revisão interna final (qualidade e marca) | R | A | I | — | C | — |
| Checagem de políticas (anúncio, LGPD, imagem, CONAR) | R | A | C | — | C | C |
| Envio para aprovação | R | A | I | I | — | — |
| Aprovação da peça | I | I | C | **A/R** | — | — |
| Consolidação do feedback | R | A | C | C | I | — |
| Ajustes na peça | C | I | — | — | R | — |
| Escalonamento de atraso | R | A | R | C | — | — |
| Liberação de peça de mídia paga (POP) | C | A | C | R | — | R |

R = executa · A = responde pelo resultado · C = consultado · I = informado

## Agentes de apoio e o que pedir

| Agente | Quando usar | Prompt curto |
|---|---|---|
| 🎨 Brand Guardian | Antes do envio ao Cliente | "Revise esta peça e legenda contra o guia de marca e o tom de voz de [CLIENTE]. Liste desvios de cor, tipografia, logo, linguagem e promessa. Classifique em bloqueante / ajuste / sugestão." |
| ✍️ Ad Creative Strategist | Peças que vão para mídia paga | "Verifique se este criativo e texto de anúncio para [PLATAFORMA: Meta/Google] respeitam as políticas de anúncio (alegações, saúde, antes/depois, preço, texto na imagem). Aponte riscos de reprovação e sugira alternativas." |

> Os agentes **apontam riscos**. A Supervisão decide o que vai ao Cliente; o Cliente decide o que é aprovado.

## Passo a passo

| # | Etapa | Responsável | Sistema | Tempo típico |
|---|---|---|---|---|
| 1 | Revisão interna final com checklist de qualidade (com apoio do Brand Guardian) | Analista | iClips / VJOB | 10–20 min por peça |
| 2 | Checagem de conformidade: políticas Google/Meta, LGPD, direito de imagem, CONAR | Analista + Supervisão | Checklist no card | 5–15 min por peça |
| 3 | Para mídia paga: aplicar o POP **VAN-POP-MKT-001 — Aprovação de Criativos de Mídia Paga** (rascunho, em aprovação) | Analista + Tráfego | Conforme POP | Conforme POP |
| 4 | Envio ao Cliente em lote organizado, com prazo de retorno explícito ([template Social → Cliente](../coordination/handoff-templates.md#social--cliente)) | Analista | WhatsApp / e-mail | 15–30 min por lote |
| 5 | Registro do envio no card (data, hora, aprovador, prazo) | Analista | VJOB / iClips | 2 min por lote |
| 6 | Lembrete ao Cliente na metade da janela e no vencimento | Analista (futuro: automático) | WhatsApp / e-mail | 2 min |
| 7 | Recebimento e consolidação do feedback em um único registro ([template Cliente → Social](../coordination/handoff-templates.md#cliente--social)) | Analista | iClips (card da peça) | 10–20 min por rodada |
| 8 | Ajustes pelo D.A. ou pelo Analista (texto) | D.A./Criação | iClips | Conforme complexidade |
| 9 | Reenvio da versão ajustada, indicando a rodada | Analista | WhatsApp / e-mail | 5–10 min |
| 10 | Aprovação final registrada (print ou e-mail anexado ao card) e status "Aprovado" | Analista | VJOB / iClips | 2–5 min |
| 11 | Escalonamento se prazo ou limite de rodadas estourar ([template Escalonamento de atraso](../coordination/handoff-templates.md#escalonamento-de-atraso)) | Analista → Supervisão | Google Chat / VJOB | Imediato |

### Janela de retorno e lembretes

| Tipo de peça | Janela de retorno do Cliente | Lembretes |
|---|---|---|
| Feed / carrossel / Reels planejado | até 2 dias úteis (meta sugerida — validar) | 1º na metade da janela; 2º no vencimento |
| Stories recorrentes e ofertas diárias | até 4 horas úteis (meta sugerida — validar) | 1 lembrete antes do horário de publicação |
| Peça de mídia paga | conforme POP VAN-POP-MKT-001 | conforme POP |
| Campanha sazonal | definido no cronograma da campanha | a cada marco |

Se a janela vencer sem resposta, **a peça não é publicada**. O Analista registra "Aguardando Cliente" no card e aciona o Account.

### Limite de rodadas e escalonamento

- Até **2 rodadas de ajuste** por peça dentro do escopo (meta sugerida — validar).
- A 3ª rodada exige ciência da Supervisão e é registrada como possível extra.
- Mudança de briefing depois da aprovação da pauta volta para a [Fase 2](fase-2-planejamento-mensal.md) ou é tratada como demanda extra.

```
Escalonamento (atraso de aprovação ou rodadas acima do limite)
Analista de Social ──► Supervisão de Social Media ──► Account ──► Diretoria de Operações
   (lembretes)          (prioriza e renegocia data)   (aciona Cliente)   (casos graves / impacto de escopo)
```

### Checagem de conformidade (mínimo)

- **Políticas de anúncio Google e Meta**: alegações de saúde e resultado, antes/depois, preço e condições, segmentação sensível, texto em excesso na imagem.
- **LGPD**: nenhum dado pessoal de consumidor exposto (nome, telefone, CPF, prints de conversa sem anonimização).
- **Direito de imagem**: autorização de uso de imagem de colaboradores, clientes finais e influenciadores; licença de fotos, fontes e músicas.
- **CONAR**: publicidade identificada (#publi quando houver parceria), sem comparativo enganoso, cuidado reforçado com público infantil, bebidas e medicamentos.

### Apresentação de aprovação

Quando a conta aprova por apresentação (PPT ou PDF), use um modelo único: capa com cliente e período → uma página por peça (arte, legenda, data, canal) → campo "aprovado / ajuste" por peça → página final com prazo de retorno. O cliente responde no mesmo arquivo ou por escrito no canal oficial, e a resposta vai para o card.

### Feedback do cliente → checklist de ajustes

Feedback que chega em várias mensagens, ou perto da publicação, gera retrabalho. O Analista cola as mensagens da rodada (sem dados pessoais) e pede ao **Content Creator** uma lista numerada de ajustes por peça, apontando conflitos entre pedidos. Essa lista é confirmada com o cliente antes de ir à Criação e é registrada no card ([Cliente → Social](../coordination/handoff-templates.md#cliente--social)). Feedback de última hora fora da janela combinada entra como nova rodada.

## Quality Gate G4

- [ ] Checklist interno de qualidade concluído e anexado ao card
- [ ] Brand Guardian consultado e desvios bloqueantes resolvidos
- [ ] Conformidade conferida: políticas Google/Meta, LGPD, direito de imagem, CONAR
- [ ] Peças de mídia paga passaram pelo fluxo do POP VAN-POP-MKT-001
- [ ] Aprovação **escrita** de aprovador **autorizado** registrada no card (print/e-mail)
- [ ] Feedback consolidado em um único registro por card, com número da rodada
- [ ] Versão aprovada é a mesma que será publicada (arquivo e legenda finais)
- [ ] Status do card atualizado para "Aprovado" no VJOB/iClips
- [ ] Nenhuma peça segue para a Fase 5 sem os itens acima

## Riscos e como mitigar

| Risco (dor) | Mitigação |
|---|---|
| Atraso por dependência de aprovação (ALTA) | Envio em lote com prazo explícito, lembretes programados, escalonamento em cadeia, calendário aprovado antes do mês |
| Feedback fragmentado em vários canais (MÉDIA) | Um único registro por card; Analista transcreve áudio/ligação para texto e pede confirmação escrita |
| Aprovação por pessoa não autorizada | Lista de aprovadores no onboarding; revisão da lista a cada trimestre (meta sugerida — validar) |
| Rodadas infinitas de ajuste | Limite de rodadas, registro como extra, alinhamento via Account |
| Reprovação da plataforma de anúncio | Checagem prévia com Ad Creative Strategist e POP de mídia paga |
| Publicar versão errada | Nome de arquivo com versão (v1, v2, final) e conferência no checklist |
| Volume simultâneo de envios (ALTA) | Janelas fixas de envio por cliente; priorização diária pela Supervisão |

## Oportunidades de automação e IA

- **Fluxo de aprovação com status, lembrete e histórico** (pedido do time): status no card (Enviado / Em ajuste / Aprovado / Vencido), lembrete automático ao Cliente e trilha completa.
- **Alertas de prazo e atraso no VJOB** para peças "Aguardando Cliente" perto do horário de publicação.
- **Consolidação assistida**: IA (ChatGPT/Claude) resume mensagens e áudios transcritos em lista numerada de ajustes; o Analista confere antes de passar ao D.A.
- **Pré-checagem de conformidade** com Brand Guardian e Ad Creative Strategist em lote.
- **Biblioteca de prompts** de revisão por tipo de peça.

> Toda saída de IA é revisada por humano antes de ir ao Cliente ou ao D.A.

## Indicadores da fase

| Indicador | Meta |
|---|---|
| Peças aprovadas dentro da janela de retorno | ≥ 85% (meta sugerida — validar) |
| Média de rodadas de ajuste por peça | ≤ 1,5 (meta sugerida — validar) |
| Peças publicadas sem aprovação registrada | 0 (obrigatório) |
| Tempo médio entre envio e aprovação | ≤ 2 dias úteis (meta sugerida — validar) |
| Reprovações por política de anúncio | ≤ 5% das peças de mídia (meta sugerida — validar) |
| Escalonamentos à Diretoria de Operações por mês | acompanhar tendência (meta sugerida — validar) |

## Handoff para a próxima fase

Com G4 aprovado, a peça segue para a [Fase 5 — Publicação, Comunidade e Mídia Paga](fase-5-publicacao-e-midia.md).

- Peças orgânicas: card com status "Aprovado", arquivo final, legenda final, data e hora.
- Peças de mídia paga: usar o template [Social → Tráfego](../coordination/handoff-templates.md#social--tráfego).
- Fechamento do gate: template [Fechamento de fase](../coordination/handoff-templates.md#fechamento-de-fase).

Voltar ao documento-mestre: [Ciclo de Operação da Agência](../ciclo-agencia.md) · Fase anterior: [Fase 3 — Produção Criativa](fase-3-producao.md)

---

<sub>Adaptado do NEXUS (playbook de hardening de software) para a operação de agência.</sub>
