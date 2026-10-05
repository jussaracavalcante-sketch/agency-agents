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


---

# Rodada de validação de 02/10 (build `a57e0ae`): primeiro piloto com portões humanos concluído

Execução `98264951` encadeada até `242f9767`: **21 de 21 tarefas, estado SUCCESS**, com G1, G2 e G3 respondidos
("Aprovado." como teste; publicação real desligada). Um único resume por portão.

| Verificação | Resultado |
|---|---|
| Pausa e retomada nos 3 portões | OK, sem erro de plataforma |
| Histórico de feedbacks nos pedidos | OK ("Nenhum feedback humano recebido"; sem feedback fabricado) |
| Guardião reprova com citação literal | OK (calendário e plano de mídia reprovados no G2) |
| `aplicacao_g2` reemite peças liberadas e bloqueia as reprovadas | OK (conteúdo web e e-mail reemitidos; calendário e mídia bloqueados) |
| `aplicacao_g3` com Guardião reprovado | OK (nenhum canal autorizado, orçamento R$ 0) |
| `execucao_publicacao` | OK ("NÃO EXECUTADO"; nenhuma publicação) |

Falhas de conteúdo observadas nessa rodada (corrigidas no build seguinte): canal "Instagram" para o artigo e datas
inventadas no roteiro; reemissão do conteúdo web acrescentou "garantindo segurança e precisão diagnóstica";
sumário descrevia e-mail como "pronto para envio" e G3 como "aprovado com restrições severas"; pedido do G3 listava
orçamento do plano de mídia bloqueado.

Erro anterior no mesmo dia: guardrail do portão derrubou uma execução ao reexecutar a tarefa no resume
(`guardrail validation after 2 retries`). Corrigido com limite de rejeições; execução concluída zera a contagem da regra
de rollback.

---

# Validação final de 02/10 (build `1768574`): fluxo funcional

Execução `f1c67ab2` encadeada até `b2a90978`: **21 de 21 tarefas, SUCCESS**. Quinta rodada seguida concluída
(contador da regra de rollback: 0 de 2). G1, G2 e G3 respondidos com "Aprovado." como teste; publicação real desligada.

| Verificação | Resultado |
|---|---|
| Pausa e retomada nos 3 portões, um resume por portão | OK |
| Depoimento, testemunho, caso de sucesso, paciente real nas peças | Nenhuma ocorrência |
| Líder, referência, premiado, "o melhor hospital" nas peças | Nenhuma ocorrência (só no registro de remoção) |
| Garantia de segurança, precisão ou resultado | Nenhuma ocorrência |
| Cirurgia robótica | Só no mapa SEO, como tendência setorial; fora do brief e das peças do cliente |
| Datas completas inventadas fora do calendário | Nenhuma ("a definir") |
| Calendário editorial | 24 posts, 01/11 a 20/12, as 8 semanas, em formato compacto |
| G3 com Guardião reprovado | "BLOQUEADO: NENHUM CANAL AUTORIZADO", orçamento R$ 0 |
| Publicação | "NÃO EXECUTADO", roteiro com datas "a definir" |

Salvaguardas ativas: guardrails em código (cópia literal do parecer, claims proibidos, calendário completo, serviços
fora do briefing), cada um com limite de duas rejeições para não derrubar a execução.

Limites que permanecem: a lista de termos de serviços é fixa; o Guardião (LLM) ainda não pega tudo, por isso o código
é a barreira confiável; o texto de aprovação ("Aprovado.") não carrega instruções, que só chegam à aplicação pelo
histórico de devoluções; a publicação real segue desligada até haver um G3 aprovado por pessoa.


---

# Primeiro piloto pelo portal (02/10, execução `621ded65`)

Disparado pelo portal às 22:26 UTC, build `1768574`. G1 e G2 aprovados com "Aprovado." (sem instruções); G3 pendente na
data do registro. Publicação real desligada.

| Verificação | Resultado |
|---|---|
| Disparo, portões e retomadas encadeadas pelo portal | OK; cliente e decisões registrados no banco |
| Brief usou o objetivo do briefing | **Falhou**: trocou por "+20% de agendamentos" |
| Baselines | **Falharam**: "100 consultas mensais" e "70% de ocupação" ("registros internos") não constam dos insumos |
| Peças com superlativos e garantias | **Falharam**: "o melhor atendimento", "tecnologia de ponta", "última geração", "garante precisão", "garante aderência à LGPD", "diagnósticos precisos e tratamentos eficazes" |
| Placeholder | **Falhou**: link `https://example.com/cta-button` na peça reemitida |
| Calendário reemitido | Só 2 linhas (não cobriu as 8 semanas) |
| G3 | Guardião reprovou o pacote; nada autorizado para publicação |

Causa comum: "Aprovado." não carrega instruções; as reprovações do Guardião só viram correção se o humano devolver com
texto. As travas em código existem para barrar o que o Guardião (LLM) deixa passar.

## Travas acrescentadas depois desta rodada
- Claims: "o/a/ao melhor", "melhor atendimento/cuidado/experiência", "tecnologia de ponta", "última geração", "estado da
  arte", "diagnósticos precisos", "tratamentos eficazes", "confiança em cada diagnóstico", "segurança em cada tratamento" e
  `garante/garantindo ... precisão|segurança|excelência|qualidade|resultado|LGPD|conformidade|aderência...`.
  Linha com [VALIDAR] ou aviso de proibição continua passando.
- Placeholders (`example.com`, `exemplo.com`, `lorem ipsum`, `[inserir ...]`) barrados nas peças de produção e na
  reemissão do G2.
- Brief: precisa reproduzir o objetivo do briefing literalmente e não pode trazer baseline com números fora dos insumos.
- Calendário reemitido na `aplicacao_g2`: se a reemissão trouxer o calendário, ele precisa cobrir todas as semanas (datas dd/mm/aaaa ou
  aaaa-mm-dd, "Semana N" ou coluna numérica de semana). Calendário não reemitido não é cobrado.
- Testes em `tests/test_guardrails.py`.

Limite: cada trava aceita a saída depois de duas rejeições (para não derrubar a execução), então ela reduz mas não
elimina o risco; o G2 e o G3 humanos continuam sendo a barreira final.


## Rubrica do revisor de qualidade (fase 1 da integração do squad)
Acrescentados o agente `revisor_qualidade` (13º) e a tarefa `rubrica_qa` (22ª do pipeline), antes da revisão do G2, com guardrail
de formato e coerência (gates, nota, veredito, selo AVAL MÉDICO em saúde) e cópia literal do quadro de notas no pedido do G2.
Ainda não validada em execução. Se o próximo piloto falhar duas vezes, vale a regra de rollback (base `8fa07e3`).


# Segundo piloto com rubrica (05/10, execução `e3b795a7`, build `8bc1cbad` / `d590968`)
G1 aprovado com "Aprovado." e G2 pendente na data do registro. Objetivo literal e baselines do briefing: **OK**. Fonte "Análise interna do
Hospital Santa Júlia" inventada (o Guardião pediu a correção e a aplicação a incluiu): **falhou**.

| Peça | Rubrica do Rui | Guardião | Conferência por trecho literal |
|---|---|---|---|
| Conteúdo web | 97 APROVAR | Aprovado com ajustes | "infraestrutura de ponta", "Sua Melhor Escolha", "Escolha Segura", "precisão e segurança nos tratamentos", nota interna "reformulei o conteúdo" |
| Calendário | 100 APROVAR | Aprovado | 8 semanas completas; pilar "Acolhimento Premium" e hashtags #SaudePremium (decisão humana) |
| E-mail | 59 REFAZER (G1 e G3) | Reprovado | "o melhor atendimento em saúde", "acolhimento premium que você merece" não citados pela rubrica |
| Mídia | 98 APROVAR | Aprovado | Meta Ads e LinkedIn Ads fora do brief aprovado; CPC/CTR/CVR sem fonte; conversões 100/200/300 não batem (75/120/187) |

Conclusão: a rubrica funciona no formato e nas faixas, mas foi leniente e ancorou o Guardião (que deixou de apontar o que apontava antes).

## Melhorias de trava (pós-rodada)
- Rubrica passa por varredura em código: se achar superlativo, garantia, placeholder, nota interna, canal fora do brief ou conversões que não
  fecham numa peça, a linha RESUMO não pode marcar G1 e G3 como OK sem citar o trecho nos apontamentos.
- O Guardião do G2 revisa de forma independente: a rubrica saiu do contexto dele e continua ao lado, no pedido do portão.
- Notas internas do agente dentro da peça ("reformulei", "conforme solicitado") barradas.
- Plano de mídia: canal fora do brief, projeção sem [VALIDAR] e conversões fora de verba ÷ CPC × CVR (tolerância de 15%) rejeitados.
- Brief: fonte do baseline que o briefing não cita ("análise interna", "registros internos") rejeitada.
- Termos novos: "de ponta", "melhor escolha", "escolha preferencial", "escolha segura", "precisão e segurança", "certificações reconhecidas".
  "Premium" e "excelência" ficam fora da trava (decisão: rubrica e G2 humano).
