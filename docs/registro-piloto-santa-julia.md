# Registro do piloto: Hospital Santa Júlia (execução com portões humanos)

Data: 2026-10-02. Build: `f3fd887` + correção dos gates (`1004293`). Execução original `18392b0c`, encadeada por resumes até `d8754cb5`.

## Decisões humanas registradas

| Portão | Decisão | Observação |
|---|---|---|
| G1 | Devolvido com feedback (5 ajustes) e depois aprovado | O brief reemitido cumpriu 4 dos 5 ajustes. Tom e termos da marca não ficaram como [VALIDAR]. |
| G2 | Devolvido com feedback (6 ajustes) e depois aprovado | A `aplicacao_g2` só emitiu o registro de decisão e não reemitiu nenhuma peça. O calendário foi liberado com datas fora do período. |
| G3 | **Reprovado** (parecer do Guardião: Reprovado) | Nenhum resume foi enviado: a plataforma trata qualquer texto diferente de "Aprovado." como retrabalho. A execução fica pausada e nada é publicado. |

## O que o piloto validou
- Execução ponta a ponta até o G3, com 21 tarefas e webhooks capturados no Supabase.
- Pausa humana real nos três portões e resume com feedback e com "Aprovado.".
- O parecer do Guardião passou a ser reproduzido literalmente no pedido dos portões.
- A regra da pior dimensão no parecer funciona.

## O que o piloto reprovou
- O pedido do G3 fabricou um feedback humano que ninguém escreveu.
- A `aplicacao_g2` não reemite as peças ajustadas. O fluxo não tem tarefa de retrabalho após o G2.
- As peças reintroduziram datas, canais, orçamento e fontes fora do brief aprovado, e a revisão do G2 não barrou.
- Aprovação sem instruções não carrega correções: elas só chegam à tarefa de aplicação pelo histórico de feedback do portão.
- Um resume encadeado falhou na plataforma (`NoneType` em `crew_reload`), sem causa confirmada.

## Correções necessárias antes de novo piloto
1. Histórico de feedbacks dos portões: só o que o humano escreveu; sem feedback, "nenhum".
2. `aplicacao_g2`: reemitir integralmente cada peça que recebeu ajuste.
3. Revisão do G2: conferir datas, canais, orçamento e fontes contra o brief aprovado.
4. Brief e peças: respeitar o período e os canais do brief.
5. Antes de publicar qualquer peça de saúde: validação médica e do responsável técnico.
