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


# Terceiro piloto com rubrica (05/10, execução `7ebd5877`, build `bc3ef896` / `5d9e3f9`)
G1 e G2 aprovados com "Aprovado." e G3 pendente com parecer Reprovado do Guardião; publicação desligada.

| Verificação | Resultado |
|---|---|
| Objetivo geral literal e baseline 863/343 | OK |
| Fonte do baseline | "Relatório interno RD Station": inventada; objetivo específico de +20% de tráfego com baseline "1.000 visitas semanais" e Google Analytics: inventado |
| Rubrica do Rui (varredura em código) | **Funcionou**: as quatro peças saíram 59 DEVOLVER (G1 em FALHA em conteúdo, calendário e mídia; G2/LGPD no e-mail), com trechos reais |
| Guardião independente | Divergiu da rubrica (mídia "Aprovado com ajustes"); o pedido do G2 mostra os dois |
| Parecer do G1 | "Resultado Geral: Aprovado com ajustes" com dimensão Reprovada: contraria a regra do pior resultado |
| Peças | Ainda com "tecnologia de ponta", "infraestrutura de ponta", "referência em", "garantindo segurança", "melhor pra você": travas esgotaram as 2 tentativas e aceitaram |
| G3 | Pedido com parecer resumido (não literal) e abertura de comentário na `aplicacao_g2` |

## Melhorias (pós-rodada)
- **Alerta de trava esgotada**: quando uma trava reprova 3 vezes, a saída é aceita com uma linha `ALERTA DE QUALIDADE` no topo com a pendência.
  As varreduras ignoram essa linha. Os pedidos dos portões listam os alertas (instrução nos prompts) e o portal os mostra em destaque
  na tela de aprovação (caixa vermelha e contador na lista).
- Projeções de CPC/CTR/CVR em **lista** (além de tabela) exigem [VALIDAR].
- "no/na melhor" e "melhor pra/para você" entram nos superlativos.
- `revisao_g1`: o Resultado Geral precisa ser o pior entre as dimensões.
- Abertura de conversa do agente ("Para proceder…", "Abaixo está…") rejeitada em todo documento.
- Fica para depois: cenários de orçamento do brief somarem exatamente o total do briefing.

# Quarto piloto com rubrica (05/10, execução `c3298b2a`, build `8723f3c`)
G1 aprovado com "Aprovado." (parecer Reprovado e alerta no brief); a execução seguiu para as peças.

| Verificação | Resultado |
|---|---|
| Alerta de trava esgotada | **Funcionou**: linha `ALERTA DE QUALIDADE` no topo do brief, no pedido do G1, em conteúdo ("de ponta") e em mídia |
| Resultado Geral do parecer do G1 | Reprovado e coerente com as dimensões (regra do pior resultado) |
| Objetivo literal | Falhou após 3 tentativas ("...ao longo da campanha de 8 semanas") |
| Fonte | "CRM do Hospital Santa Júlia" inventada |
| Orçamento e hipóteses | Tabela por canal inventada, ignorando a verba de mídia do briefing; "+40%" e "+20%" sem [VALIDAR]; "Total R$ 25.000" sem o [VALIDAR] do briefing |
| Mensagem da trava | O agente a tratou como feedback humano e comentou "conforme o feedback recebido" no brief |

## Melhorias (pós-rodada)
- Abertura "Vamos…" entra na lista de aberturas de conversa rejeitadas.
- Fontes: "CRM do <cliente>", "sistema de CRM", "Google Analytics", "Search Console", "dados do hospital" e "sistema interno" rejeitadas quando o briefing não os cita.
- Percentual novo no brief (meta, hipótese, divisão de orçamento) exige [VALIDAR] na mesma linha.
- O brief precisa citar a verba de mídia do briefing e manter o [VALIDAR] dos valores que o briefing marca assim.
- Toda rejeição de trava chega ao agente com o prefixo "REVISÃO AUTOMÁTICA DE QUALIDADE (não é feedback humano…)"; o alerta mostra o motivo sem o prefixo.
- Objetivo literal pedido em bloco de citação (`> objetivo`), sem objetivo específico, e orçamento sem divisão inventada (a divisão restante vai [VALIDAR]); `aplicacao_g1` passa pela mesma trava do brief.

# Quinto piloto com rubrica (05/10, execução `8e11e98c`, build `2929969e` / `4451e6e`)
G1 aprovado com "Aprovado." 56 s depois da pausa; execução seguiu para as peças.

| Verificação | Resultado |
|---|---|
| Alerta de trava no brief | **Nenhum** (rodada anterior: 3 até o G1) |
| Objetivo literal em bloco de citação, fonte Nekt, percentuais e verbas com [VALIDAR] | **OK** |
| Parecer do Guardião | Reprovado, com falhas: dimensão "Coerência" Reprovada com apontamento "nenhuma correção necessária"; reprova por itens já marcados [VALIDAR]; citação deturpada ("conhecimento da diferença que um atendimento…" no lugar de "Conheça a diferença…") |
| Brief | Parágrafo depois do documento com autocertificação ("seguindo rigorosamente as diretrizes"); "Dados de Mercado: CFM, ANVISA, CONAR" |
| `aplicacao_g1` | Alerta (percentual 20% sem [VALIDAR]); disse "não há ajustes pendentes" e perdeu [VALIDAR] do brief original |

## Melhorias (pós-rodada)
1. Guardião (G1 e G2): [VALIDAR] já marcado é pendência humana ("Aprovado com ajustes"), não reprovação; só reprova item inventado sem marcação e sem fonte.
2. Parecer (G1, G2, G3): todo trecho entre aspas precisa existir no texto revisado (código compara; linhas de regra ou correção sugerida não contam).
3. Dimensão Reprovada cujo apontamento diz "nenhuma correção necessária" ou "está coerente" é rejeitada.
4. Texto depois do fechamento do bloco ``` e frases de autocertificação ("seguindo rigorosamente", "todos os feedbacks foram incluídos", "não há ajustes pendentes") rejeitados.
5. Órgãos reguladores (CFM, ANVISA, CONAR) como fonte de "dados de mercado" rejeitados no brief.
6. `aplicacao_g1`: sem feedback humano escrito, a reemissão não pode ter menos marcações [VALIDAR] que o brief original.

# Rotina de Mídia Paga e Performance parametrizada (05/10)
Acrescentados o agente `supervisor_midia_paga` (14º) e a tarefa `auditoria_midia` (23ª do pipeline), antes da direção de arte e da rubrica; `gestor_midia_paga` e
`analista_dados` reescritos com a rotina de Carlos André e João Araújo; parâmetros em `config/rotina_midia.yaml`. Trava do plano de mídia exige budget pace, alerta de
90%, UTM, revisão técnica do Supervisor e alçadas. Detalhes em `docs/rotina-midia-paga.md`. Ainda não validada em execução; se o próximo piloto falhar duas
vezes, vale a regra de rollback (base `8fa07e3`).

# Sexto piloto: rotina de mídia (05/10, execução `7d989de1`, build com a rotina)
Decisões humanas: G1 devolvido e depois aprovado; G2 "Aprovado." sem texto; G3 reprovado. A esteira foi do briefing ao G3 sem erro técnico (19 tarefas, 3 pausas
retomadas). Falhas de qualidade que as travas sinalizaram mas não impediram: cinco tarefas aceitas com ALERTA DE QUALIDADE (`aplicacao_g1`, `producao_conteudo`,
`plano_midia_paga`, `aplicacao_g2`, `portao_g2`); rubrica com REFAZER em conteúdo, e-mail e mídia e G2 aprovado sem correções; `aplicacao_g2` em inglês antes e depois do
documento e com calendário de 3 linhas (a trava aceitava a "semana 8" citada); e-mail reemitido só com [VALIDAR]; direção de arte com depoimento de paciente inventado;
pacote de publicação montado com o calendário substituído (5 semanas, 12 de 15 datas "a definir").

## Melhorias (pós-rodada)
1. Frase em inglês fora de tabela/código rejeitada em toda tarefa de documento (`_linha_em_ingles`).
2. Cobertura do calendário exige semanas distintas e ao menos 2 posts por semana; citar a última semana não basta.
3. `aplicacao_g2`: sem ajustes escritos pelo humano ("Aprovado."), peça com VEREDITO=REFAZER na rubrica tem de constar como bloqueada.
4. `pacote_publicacao`: posts de rede social só com datas do calendário vigente (reemitido, se houver), sem "a definir" onde há data e cobrindo a campanha inteira.
5. Portal: confirmação antes de enviar a decisão (mostra o texto enviado) e execução reprovada passa a constar como encerrada.

# Sétimo piloto (05/10, execução `9b423a64`, build `ffcc3d4`)
Decisões humanas: G1 "Aprovado." sem texto; G2 registrado como "Aprovado." sem texto; G3 registrado como Reprovar (com texto de ajustes gravado só como justificativa). Sem erro técnico.
Resultado das travas do sexto piloto: sem inglês, calendário com 8 semanas (24 posts), conteúdo e mídia bloqueados no G2 por REFAZER na rubrica, pacote sem peça do calendário
substituído. Falhas que restaram: 8 alertas de qualidade (brief, parecer G1, aplicação G1, produção, calendário, mídia, aplicação G2, revisão G3); "cirurgia robótica" e
"telemedicina" no brief e nas peças; calendário com datas passadas (02 e 03/10) e linha solta dentro da tabela; mídia com YouTube Ads e Display.

## Melhorias (varredura de QA após a rodada)
1. Saneador na última tentativa (`_com_limite_de_rejeicoes(..., saneador=...)`): quando a trava esgota, a saída aceita já sai com serviço fora do briefing trocado por
   `[VALIDAR: serviço fora do briefing]`, afirmação proibida marcada `[VALIDAR MÉDICO]` e, no plano de mídia, canal fora do brief trocado por `[VALIDAR: canal fora do brief]`.
   O alerta no topo lista o que foi trocado. Na reemissão do G2 só o trecho reemitido é saneado (o registro que cita o problema fica intacto).
2. Calendário: data anterior a hoje (fuso da campanha) e linha de tabela com número de colunas diferente do cabeçalho são rejeitadas (também na reemissão do G2).
3. Portal: Aprovar ou Reprovar com texto digitado exige confirmar que o texto não será enviado (servidor responde 409 sem a confirmação).
Não resolvido: divergência entre rubrica e Guardião (e-mail 98 na rubrica com número inventado) e parecer do Guardião sem citações; ficam como risco conhecido para o G2/G3 humano.

# Oitavo piloto (05/10, execução `c344956d`, build `2a7c612`)
G1 limpo (sem alerta, sem "cirurgia robótica"). G2 devolvido com texto (decisão registrada corretamente como Devolver) e aprovado no segundo pedido. A `aplicacao_g2` **não aplicou** os
ajustes: respondeu que não conseguiu obter o feedback (que estava no pedido do portão) e a trava de tamanho esgotou, então a recusa seguiu adiante como saída aceita e o pacote foi montado
com as peças antigas (datas 02/10 a 06/10, já passadas). Lacunas também achadas: calendário com datas sem ano passou pela trava de data passada; "não há necessidade de alteração" não era
reconhecido como dimensão sem problema.

## Melhorias (pós-rodada)
1. Frases de recusa ("não consegui obter", "recomendo verificar o acesso", "equipe de TI") entram em `_FRASES_DE_FALHA`.
2. `aplicacao_g2` esgotada com saída curta ou recusa vira registro honesto "aplicação NÃO EXECUTADA": nenhuma peça reemitida, todas bloqueadas, feedback humano copiado literalmente.
3. `pacote_publicacao`: com aplicação não executada, o cronograma não pode listar posts.
4. Datas dd/mm sem ano valem como do ano corrente (cobertura e data passada); `_SEM_PROBLEMA` reconhece "não há necessidade de alteração" e "não apresenta alterações".

## Melhorias (itens 3 a 5 do relatório do oitavo piloto)
1. Plano de mídia: quando a trava esgota, as seções da rotina que o plano omitiu ("Insumos e pendências", "Rotina operacional (diária, semanal)" com budget pace, alerta aos 90% e UTM, "Alçadas e autorizações")
   são inseridas por código a partir de `config/rotina_midia.yaml`, marcadas como inseridas automaticamente para o gestor revisar.
2. Saneador: o serviço fora do briefing vira "serviço [VALIDAR: confirmar com o hospital]" com o artigo ajustado ("A telemedicina proporciona" → "O serviço [VALIDAR…] proporciona"), em vez de deixar a frase quebrada.
3. Rubrica: FALHA que cita trecho já marcado [VALIDAR], ou "Compliance e precisão" ≤ 5/20 por causa do marcador, é rejeitada; o prompt da tarefa diz o mesmo.

# Nono piloto (05/10, execução `b8a53b9b`, build `fa5dafd`): G1
Brief sem alerta, mas com falhas que as travas não viam: fontes inventadas ("Tendências: Anahp e Estadão"), marcador falso "R$ 11.654 [confirmado]" (o briefing só traz esse valor como consumo
dos últimos 90 dias), frases de garantia ("A escolha certa") e nota de conformidade dentro do bloco de código ("Todos os elementos foram desenvolvidos em conformidade com o guia").

## Melhorias
1. Brief: nome próprio na seção Fontes que o briefing e a base do cliente não citam é rejeitado (`_fontes_nao_informadas`); na última tentativa a linha vira `[VALIDAR: fonte]`.
2. Marcadores que não existem ([confirmado], [validado], [aprovado], [ok]) rejeitados; viram [VALIDAR] na última tentativa.
3. Autocertificação ampliada ("todos os elementos foram…", "desenvolvidos em conformidade", "respeitando a linguagem de"), inclusive dentro do bloco; a nota é removida na última tentativa (`_sanear_brief`).

# Nono piloto: produção e G2 (execução `b8a53b9b`, retomada `0a44840d`)
G1 aprovado sem o texto (o portal registrou Aprovar com o texto guardado, não enviado). A `aplicacao_g1` reescreveu o brief mesmo sem feedback, declarou "ajustes aplicados" que ninguém pediu e
introduziu "tecnologia de ponta". Calendário veio com datas "01-Nov-23" (2023) e três posts no mesmo dia; a rubrica puniu o próprio marcador que o saneador inseriu; o conteúdo longo tratou de
telemedicina (fora do briefing) e o saneador deixou o artigo sem assunto. Plano de mídia com TikTok Ads e Display (trocados) e as seções da rotina inseridas por código.

## Melhorias
1. `aplicacao_g1` sem feedback humano: precisa reproduzir o brief original (≥ 70% das linhas); ao esgotar, o brief original saneado segue com "Ajustes aplicados: nenhum".
2. Calendário: datas em formato dd-Mon-aa reconhecidas (e 2023 acusado como passado); tabela com menos de metade das datas legíveis é rejeitada.
3. "Segurança em cada diagnóstico" entra nos claims; "Garantir …" em item de checklist deixa de ser tratado como promessa.
4. Portal: Aprovar fica bloqueado quando há texto de ajustes escrito (evita Aprovar com o texto perdido).

## Melhorias (itens do relatório do nono piloto)
1. Calendário: a tabela precisa da coluna Data; post com história, relato ou depoimento de paciente é rejeitado mesmo com [VALIDAR] em outra célula da linha (`_tabela_sem_coluna_data`, `_historias_de_pacientes`).
2. Reemissão do G2: marcador inexistente ([confirmado]) rejeitado e trocado por [VALIDAR]; o plano de mídia reemitido precisa manter a rotina (budget pace, alerta de 90%, UTM, alçadas) e, ao esgotar, as seções são inseridas por código.
3. Serviços: `before_kickoff` calcula `servicos_nao_informados` (serviços e especialidades que o briefing e a base do cliente não citam) e as tarefas de conteúdo, calendário, e-mail, direção de arte e plano de mídia o recebem no prompt como lista de itens que não podem ser tema, título, exemplo nem copy.

# Décimo disparo (05/10): recusado pela plataforma
O disparo de 17:58 foi recusado com `Missing inputs: servicos_nao_informados`. A plataforma exige todos os campos `{...}` das tarefas antes de rodar o `before_kickoff`, e o portal só envia os 17 campos do
briefing; o campo novo do item "serviços não informados" quebrou o kickoff (nenhuma execução criada, sem custo). Correção: o bloco `[SERVIÇOS NÃO INFORMADOS]` passa a ir no fim de `contexto_cliente`
(que toda tarefa já recebe), fora do texto permitido e sem duplicar em retomadas. Teste de regressão: os placeholders das tarefas e agentes só podem ser os 17 campos do briefing.

# Undécimo disparo (05/10, execução `179fec0f`, build `2048fbd`): G1
Brief sem alerta, objetivo literal, fontes só as do briefing, sem "[confirmado]", sem nota de conformidade e sem serviços fora do briefing. Pendências do brief: "visitas guiadas" e "pacotes personalizados de saúde"
sem [VALIDAR]; "exemplos de experiências de pacientes [VALIDAR]" (risco de testemunho); divisão R$ 7.000 / R$ 3.000 em [VALIDAR]. O Guardião reprovou "Coerência" escrevendo que o objetivo está coerente: a trava
`_dimensoes_incoerentes` só reconhecia títulos numerados. Corrigido: qualquer título de seção conta como dimensão.

## Undécimo disparo: produção e G2 (execução `179fec0f`)
G1 devolvido duas vezes (a primeira com o texto "devolver") e aprovado na terceira; a `aplicacao_g1` aplicou as ressalvas. Produção com 3 alertas (conteúdo, mídia, direção de arte), contra 7 na rodada anterior.
Calendário com coluna Data e datas posteriores a hoje, sem histórias de pacientes; plano de mídia com a rotina. Falha restante: frase em inglês numa célula de tabela do calendário ("Techniques for building trust…") que a
trava de idioma não via (ela pulava linhas de tabela): corrigido, agora cada célula é conferida. Rubrica deu 100/100 ao calendário e 97 ao e-mail enquanto o Guardião pediu ajustes.

## Undécimo disparo: aplicação do G2 e G3 (execução `179fec0f`)
G2 devolvido na intenção, registrado como Aprovar sem texto. A `aplicacao_g2` abriu com "I'm going to reissue each piece…" e fechou com "This reissuance accounts for…" (inglês antes e depois do documento) e a trava aceitou na 3ª tentativa;
o pacote cobriu 2 das 8 semanas, com posts inventados ("Mês da Saúde") e horário malformado ("10:00-04:00"). Melhoria: na última tentativa, `_limpar_final` remove a frase em inglês (em célula de tabela vira
`[VALIDAR: texto em inglês]`) e corta o comentário depois do último bloco, antes de o saneador de cada tarefa atuar.

## Melhorias (itens do relatório do décimo primeiro disparo)
1. Pacote de publicação: o cronograma copia todas as linhas do calendário vigente (data e rede de cada post, 8 semanas) e não pode ter post que o calendário não tem nem repetir data e rede além do calendário;
   horário com fuso colado ("10:00-04:00") é rejeitado; com o calendário social entre as bloqueadas (ou aplicação não executada), o cronograma não lista posts de rede social (`_posts_da_tabela`, `_bloqueadas_do_g2`).
2. Reemissão do G2: serviço, especialidade ou tecnologia fora do briefing é rejeitado também na reemissão (o assunto da peça não muda); "cirurgia" e derivados entram na lista de termos sensíveis e na de serviços não informados.

# Duodécimo disparo (05/10, execução `53876f22`, build `a7d28a6`): G1
Brief sem alerta, mas com a seção Fontes listando Conselho Federal de Medicina, ANVISA e CONAR com links (cfm.org.br, gov.br/anvisa, conar.org.br) que o briefing não traz (órgãos reguladores são regras do setor, não fontes de dados);
Guardião reprovou "Coerência" citando um objetivo idêntico ao do briefing. Melhorias: link ou domínio na seção Fontes que o briefing e a base não trazem e órgão regulador citado como fonte são rejeitados;
dimensão de coerência reprovada que cita trecho idêntico ao objetivo do briefing é tratada como incoerente.

## Décimo terceiro disparo (execução 53876f22): G2 aplicado e G3

- G2 devolvido (nº 44) e aprovado (nº 45): a aplicação seguiu o texto do usuário no calendário e no título do conteúdo; o plano de mídia ficou "Bloqueada" (UTM e ritmo de verba não reemitidos) e o brief não foi alterado.
- G3: o pacote de publicação saiu com alerta de qualidade e cronograma inventado (9 posts, 02–10/11) contra 24 posts do calendário vigente; revisão do G3: Reprovado.
- Correção: `_saneador_pacote_factory` refaz o cronograma por código (uma linha por post do calendário vigente, hora "a definir", fuso America/Manaus, UTM padrão) quando a trava de rejeições se esgota. Não atua se o calendário ou a aplicação estiverem bloqueados. Teste de regressão incluído (58 testes).
- Pendente: reemissão do plano de mídia pela aplicação do G2 quando o feedback pedir; "Guia Definitivo"/"Conheça histórias" no calendário; rubrica severa.

### Desfecho da execução 53876f22
Decisões: nº 43 G1 aprovar; nº 44 G2 devolver (5 ajustes); nº 45 G2 aprovar; nº 46 G3 reprovar (campo vazio, não enviada à plataforma; execução encerrada no portal). Nada foi publicado. Registro de cada decisão confere com o que foi relatado.

## Décimo quarto disparo (execução 2896d45e, versão com saneador do pacote, commit 2af9675)

Decisões: nº 47 G1 aprovar; nº 48 G2 devolver (4 ajustes); nº 49 G2 aprovar; nº 50 G3 reprovar (campo vazio, não enviada à plataforma, execução encerrada no portal). Todas conferem com o relatado. Nada foi publicado.

Melhorou: cronograma do pacote com 24 linhas, mesmas datas e canais do calendário, sem alerta (nesta rodada o modelo acertou sozinho; o saneador não precisou atuar); sem inglês nas peças; rotina de mídia inserida por código.

Pendências para o próximo PR:
- `aplicacao_g2` encolhe as peças na reemissão (conteúdo sem metadados, e-mail sem fluxos e segmentação, lista de assets removida em vez de corrigida) e não declara o orçamento do Google Ads dentro dos R$ 15.000.
- Pacote: coluna Peça repete o título do conteúdo em todas as linhas; Link, UTM e Responsável "a definir"; hora 10:00 assumida; primeiro post na data de hoje.
- (Corrigido na análise posterior) O alerta de claims NÃO era falso positivo: o modelo manteve "garantir cuidados", "tecnologia de última geração" e "de ponta" nas três tentativas e o saneador acrescentou [VALIDAR MÉDICO] à linha, como projetado. O que estava errado era só o rótulo do alerta ("Termos trocados"), que agora diz "Saneamento automático aplicado (linha marcada…)".
- Guardião: citações que não são cópia exata, trechos de versões antigas cobrados nas reemitidas, títulos em inglês e erro de grafia no parecer do G3.
- Comentário "Notas para o Diretor de Arte" depois do bloco de código no conteúdo; "Equipas" (português de Portugal).

### Correções de código após o piloto 2896d45e
- Guardião: pareamento das aspas na checagem de citações (citação curta como "última geração" criava uma "citação" falsa entre duas aspas e gerava o alerta do `revisao_g2`); títulos de seção em inglês ("Legal and Claim Compliance") barrados; instrução para revisar a versão vigente.
- Comentário depois do documento: detecta o caso de número ímpar de cercas ``` (comentário entre o fechamento e uma cerca solta) e o saneador o corta; `expected_output` do conteúdo não pede mais "notas para o Diretor de Arte" fora do bloco (ficam em `notas_visuais`).
- Português de Portugal ("equipas", "utilizadores", "ecrã", "contacto", "telemóvel") barrado e trocado por português do Brasil na última tentativa.
- `aplicacao_g2`: reemissão com menos de 60% do tamanho da original é barrada; na última tentativa a peça vira "Bloqueadas" no registro.
- Plano de mídia: gasto histórico (run-rate de N dias) não pode ser declarado como orçamento do canal; a verba do canal é parte do orçamento do briefing, [VALIDAR].
- Pacote: coluna Peça com o formato e o hook de cada post (não o título do conteúdo longo), UTM por post preenchida, hora "a definir" quando o calendário não traz horário; o saneador do pacote gera a mesma tabela.
- Testes: 65 passando.

## Varredura de QA antes do lançamento (06/10/2026)

Execução 42551a91 (G1 devolvido, nº 51; portão reaberto e não decidido): o brief trouxe divisão de orçamento inventada (R$ 6.000 e R$ 4.000), "Nota:" ao final sem bloco de código, e o Guardião reprovou a dimensão 2 sem trecho literal e escreveu "[VALIDAR NOS UM]".

Correções:
- Documento: nota final do agente ("**Nota:** …", "Observação:") reprovada e removida na última tentativa; marcador inventado ("[VALIDAR NOS UM]") reprovado e normalizado para [VALIDAR].
- Brief: valor em R$ sem [VALIDAR] que não consta do briefing, dos inputs nem da base é reprovado; o saneador acrescenta [VALIDAR].
- Guardião: dimensão ou entrega Reprovada sem trecho entre aspas é reprovada (regra de evidência em código).
- Claims: "guia definitivo" barrado. Calendário: hook deve ser frase completa com sujeito e verbo.

Verificação: 68 testes; crew carregada com o CrewAI 1.15.23 em venv local (14 agentes, 23 tarefas, 23 guardrails, 3 portões com human_input), `before_kickoff` com o briefing de 17 campos, interpolação de todas as tarefas sem placeholder faltando; portal com `tsc` limpo e produção na Vercel em `main` 67b4463.

## Décimo quinto disparo (execução af286084, build 092fd05b, commit b454dd2)

Decisões: nº 53 G1 devolver (display, run-rate como histórico, Fontes); nº 54 G1 aprovar; nº 55 G2 aprovar (sem análise prévia); nº 56 G3 reprovar. Nada publicado.

Funcionou: aplicação do G1 aplicou os três ajustes; rubrica equilibrada (conteúdo 91); travas novas atuaram (reemissão resumida bloqueada, inglês após o documento removido, citação inexistente do Guardião no G3 acusada); pacote com Peça e UTM por post e hora "a definir".

Falhou: `aplicacao_g2` entregou esqueleto ("[O conteúdo completo original com ajustes…]", "...") e manteve "Liberadas" contraditório; pacote montou cronograma sem calendário vigente válido (reemissão sem tabela) com datas ISO não comparadas; plano de mídia com "PMax e YouTube" e run-rate como orçamento na mesma linha; Guardião do G3 reprovou UTM por "a definir após a publicação"; alerta falso na seção Fontes ("Este"); coerência reprovada com objetivo conforme; autoavaliação final no brief.

Correções (este PR): esqueleto de reemissão reprovado e, na última tentativa, peça retirada das liberadas; todas as listas "Bloqueadas" lidas; pacote usa o calendário original quando a reemissão não tem tabela e compara datas ISO; PMax/Performance Max/YouTube/Demand Gen como canais fora do brief; run-rate rotulado como orçamento reprovado; "a definir" não sustenta reprovação do Guardião (prompt e código); autoavaliação final barrada; "garanta aderência à acessibilidade" não é claim; início de frase na seção Fontes não é nome próprio. 73 testes.

### Simulação de ponta a ponta (06/10/2026)
Reexecução das travas atuais sobre as 23 saídas reais da execução af286084 (ver `docs/simulacao-ponta-a-ponta.md`). Encontrou e corrigiu: objetivo com ponto final não casava na regra de coerência do Guardião; autoavaliação pegava copy legítima; saneador do pacote mantinha posts com calendário bloqueado. 75 testes.

## Décimo sexto disparo (execução 03d3065a, deploy d2bbe83/8b120d1, Hospital Santa Júlia): relatório final

Janela: 15:50 a 17:49 UTC de 07/10/2026 (cerca de 2 h). Cadeia de execuções após as retomadas: 03d3065a, 41e5d5ac, aac502c6, dc564721, d306e927, 5eebed4f. Nada publicado.

Decisões humanas (portal_decisoes): nº 66 G1 devolver (636 caracteres); nº 67 G1 aprovar; nº 68 e 69 G2 devolver (o segundo clique abriu execução paralela; aguardar a confirmação antes de repetir); nº 70 G2 aprovar; nº 71 G3 reprovar. Cliente: Santa Júlia, portanto a base VJOB (Move) não foi exercitada.

Números: 32 eventos de tarefa, 6 pedidos de decisão humana, 14 tarefas com ALERTA DE QUALIDADE. Custo e tokens: indisponíveis (a plataforma não emite esses eventos ao webhook).

### Funcionou
- Webhook autenticado v4 recebeu os eventos reais; retomada após decisão funcionou nos três portões.
- G1: caminho aprovar e caminho devolver com reescrita aplicada.
- G2: devolver seguido de aprovar, com cinco reemissões; quatro boas (conteúdo, e-mail, mídia, arte). Bloco `registro_g2` correto.
- Guardião do G3 reprovou o pacote com evidência, e a reprovação humana coincidiu com o parecer.

### Falhou
- Reemissão do calendário: 5.610 para 9.556 caracteres, oito cabeçalhos de semana, valores em R$ inventados (R$ 500 por semana, LinkedIn R$ 300) e posts de projeto social já vindos da correção, linha de autocertificação, "Excelência médica" nas palavras-chave.
- "Ajustes aplicados" do `registro_g2`, escrito pelo modelo, descreve ajustes que não ocorreram.
- Pacote do G3: cronograma com datas (20/10, 25/10, 30/10) que não constam do calendário; resumo cita R$ 15.000 como total.
- O portão G2 mostra o texto bruto do modelo (human_input roda antes do guardrail): notas de versão e substituições feitas em código não chegam ao olhar humano.

### Backlog proposto
1. Reprovar reemissão que cresça mais de 30% e remover autocertificação.
2. Aplicar `_valores_rs_inventados` ao calendário.
3. Gerar "Ajustes aplicados" do `registro_g2` por código.
4. Prompt do portão G2 deve copiar o parecer do Guardião e incluir a nota de versão.
5. Decisão da Head: palavra-chave "Excelência médica" no Guia de Marca ([VALIDAR MÉDICO]).

### Pendências de lançamento (não técnicas)
2FA e proteção de senhas vazadas no Supabase; segundo administrador; rodar o bloco 4 de `seguranca_lgpd.sql` (expurgo de 180 dias); preencher os 23 campos [PREENCHER]/[CONFIRMAR] do aviso e do termo; confirmar cliente "Move" como Move Rental Cars; Therezinha Ruiz fora do piloto (pré-candidata, compliance eleitoral).
