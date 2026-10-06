# Simulação de ponta a ponta — Equipe de Operação de Marketing (06/10/2026)

## 1. Resumo executivo
Simulação completa do fluxo (23 tarefas, 14 agentes, 3 portões) usando as saídas reais da última execução na plataforma (af286084, build 092fd05b) como insumo e o código atual das travas (commit desta simulação) como juiz. Não houve chamada ao modelo nem à plataforma: a simulação reexecuta as travas sobre as peças reais e registra a decisão que o operador tomaria em cada portão. Resultado: o fluxo percorre as três fases sem erro de orquestração; o pacote final não sai publicável porque a aplicação do G2 reemite peças em esqueleto, e a versão atual das travas passa a bloquear essas peças e a limpar o cronograma, em vez de aceitar um pacote inconsistente. A simulação encontrou e corrigiu três defeitos adicionais (objetivo com ponto final, falso positivo em copy de e-mail, saneador do pacote com calendário bloqueado).

## 2. Método
- Insumo: 23 saídas reais da execução af286084 (Supabase, `crewai_webhook_events` 659–681), sem as linhas de alerta inseridas pelas travas.
- Juiz: funções puras de `crew.py` carregadas pelo harness de testes (`tests/test_guardrails.py`), com o briefing de 17 campos do Hospital Santa Júlia e a base de conhecimento como texto permitido.
- Portões: decisão simulada do operador segundo o critério usado nos pilotos (texto só em Devolver; Aprovar/Reprovar com campo vazio).
- Limite: a simulação não gera texto novo; onde a trava reprovaria, registra-se a reprovação e, quando existe saneador, a saída saneada da última tentativa.

## 3. Percurso do fluxo (fase → tarefa → agente → decisão)
| Fase | Tarefa | Agente | O que produz | Portão / decisão simulada |
|---|---|---|---|---|
| 1 | pesquisa_mercado | Pesquisador(a) de Mercado | relatório de mercado com [VALIDAR] | — |
| 1 | mapa_seo | Especialista em SEO | mapa de palavras-chave e pautas | — |
| 1 | brief_estrategico | Estrategista de Campanhas | brief com objetivo literal, orçamento [VALIDAR] | — |
| 1 | revisao_g1 | Guardião(ã) | parecer por dimensão | — |
| 1 | portao_g1 | Gerente de Operações | pedido de decisão G1 | **G1: Devolver** (display, run-rate como histórico, Fontes) → reabre → **Aprovar** |
| 1 | aplicacao_g1 | Estrategista | brief final com registro de decisão | — |
| 2 | producao_conteudo | Redator(a) | artigo com metadados | — |
| 2 | calendario_social | Estrategista Social | 24 posts, 8 semanas | — |
| 2 | fluxos_email | E-mail/CRM | segmentação, 3 fluxos, 3 e-mails | — |
| 2 | plano_midia_paga | Gestor(a) de Mídia | plano com rotina da Vanguarda | — |
| 2 | auditoria_midia | Supervisor(a) de Mídia | 7 linhas AUDITORIA + parecer | — |
| 2 | direcao_arte | Diretor(a) de Arte | conceito e briefings por peça | — |
| 2 | rubrica_qa | Revisor(a) de Qualidade | 4 linhas RESUMO | — |
| 2 | revisao_g2 | Guardião(ã) | parecer por entrega | — |
| 2 | portao_g2 | Gerente | pedido de decisão G2 | **G2: Devolver** (plano de mídia: só busca, verba dentro de R$ 15.000; claims marcados) → reabre → **Aprovar** |
| 2 | aplicacao_g2 | Gerente | registro + peças reemitidas | — |
| 3 | plano_medicao | Analista de Dados | KPIs, UTMs, eventos, checklist | — |
| 3 | pacote_publicacao | Coordenador(a) de Publicação | índice, cronograma, checklist | — |
| 3 | revisao_g3 | Guardião(ã) | parecer final | — |
| 3 | portao_g3 | Gerente | pedido de decisão G3 | **G3: Reprovar** (pacote sem peças reemitidas válidas; plano de mídia bloqueado) |
| 3 | aplicacao_g3 | Gerente | registro: canais autorizados = nenhum, R$ 0 | — |
| 3 | execucao_publicacao | Coordenador(a) | "NÃO EXECUTADO" | publicação desligada |
| 3 | sumario_executivo | Gerente | sumário de uma página | — |

## 4. Reexecução das travas sobre as saídas reais
| Tarefa | Agente | Na execução af286084 | Trava atual | Detalhe |
|---|---|---|---|---|
| brief_estrategico | Estrategista | alerta falso ('Este' como fonte) | passa | sem alerta falso; 'Este' não é mais nome próprio |
| revisao_g1 | Guardião | Reprovado por [VALIDAR: fonte] | reprova | A dimensão '1. Coerência com o Briefing (o trecho citado é idêntico ao objetivo do briefing)' está Reprovada, mas o próprio apontamento diz que está correta, ou só cita o objetivo do briefing (que está correto), trechos já marcado |
| aplicacao_g1 | Estrategista | autoavaliação final aceita | reprova | A saída contém link/texto de exemplo ou nota interna do agente (acreditamos que o caminho, com os ajustes realizados, está pronto para aprovação). Peça publicável não pode ter placeholder nem comentário sobre o próprio retrabalho  |
| producao_conteudo | Redator | sem alerta | passa | sem alerta |
| calendario_social | Social | sem alerta (datas ISO) | passa | sem alerta; 24 posts em 8 semanas lidos (ISO) |
| fluxos_email | E-mail/CRM | sem alerta | passa | sem alerta |
| plano_midia_paga | Gestor de mídia | alerta só pela rotina (90%) | reprova | O plano de mídia usa canal que o brief aprovado e o briefing não preveem: youtube, pmax. Use só os canais do brief aprovado; para outro canal, escreva [VALIDAR: canal fora do brief] e não aloque verba. |
| direcao_arte | Diretor de arte | alerta falso ('garanta aderência') | passa | 'garanta aderência à acessibilidade' não é claim |
| rubrica_qa | Revisor | 91/95/95/59, mídia REFAZER | passa | quadro coerente |
| aplicacao_g2 (1ª tentativa) | Gerente | esqueleto aceito com alerta | reprova | A saída traz comentário depois do documento ("Document completion is based entirely on provided instructions and gui"). O documento termina no fechamento do bloco ou na última seção: não escreva introdução, resumo, autoavaliação n |
| aplicacao_g2 (2ª tentativa, sem inglês) | Gerente | — | reprova | A reemissão é um esqueleto: "..."; "[CONTINUAÇÃO do fluxo de e-mail original, aplicando ajustes nos superl"; "[Incluindo todas as semanas da campanha com pelo menos 3 posts por sem". Não aponte para a peça original nem resuma: cop |
| aplicacao_g2 (3ª: saneador) | código | Liberadas: Conteúdo, Calendário, E-mail, Direção de Arte | aceita saneada | - **Liberadas: Direção de Arte | bloqueadas: ** Plano de Mídia - Pendência da rubrica: "Rotina operacional, projeções sem fonte"
---
 C |
| pacote_publicacao | Coordenador | 10 posts (ISO) aceitos sem alerta | reprova | O calendário social está entre as entregas bloqueadas em aplicacao_g2: o cronograma não pode listar posts de rede social. Liste só e-mail e artigo liberados, ou escreva que não há post liberado. |
| pacote_publicacao (3ª: saneador) | código | — | aceita saneada | 0 posts no cronograma (calendário original: 24); passa na própria trava: True |
| revisao_g3 | Guardião | citação inexistente; UTM reprovada por 'a definir' | reprova | A dimensão '3. UTMs Conformes (só cita trechos já marcados [VALIDAR] ou o objetivo do briefing)' está Reprovada, mas o próprio apontamento diz que está correta, ou só cita o objetivo do briefing (que está correto), trechos já marc |

Leitura: a coluna "Na execução" mostra o que a plataforma aceitou em 06/10 com o build 092fd05b; "Trava atual" mostra o que o código desta simulação faria com a mesma saída na primeira tentativa (ou, nas linhas "saneador", o que entrega depois de esgotadas as tentativas).

## 5. Defeitos encontrados pela simulação e corrigidos
1. Objetivo do briefing com ponto final não casava com a citação do Guardião: a regra de coerência incoerente não disparava na plataforma. Corrigido (comparação sem pontuação final).
2. A trava de autoavaliação ("acreditamos que…") pegava copy legítima de e-mail e a varredura da rubrica a repetia. Restrita a frases de fechamento ("acreditamos que o caminho…", "com os ajustes realizados…").
3. Com o calendário bloqueado em aplicacao_g2, o saneador do pacote deixava os posts inventados no cronograma e a saída final não passava na própria trava. Agora remove as linhas de rede social e registra o motivo.

## 6. O que a simulação não cobre
- Texto novo do modelo depois de uma reprovação: só a execução real mostra se a reemissão vem completa na segunda tentativa.
- Comportamento da plataforma (pausa, retomada, webhooks), já validado nos pilotos anteriores.
- Aval médico das peças, que permanece humano.

## 7. Próximos passos
1. Redeploy desta versão e um disparo real com análise em cada portão.
2. Critério de sucesso do próximo piloto: aplicacao_g2 sem esqueleto, pacote com 24 posts do calendário vigente, nenhum alerta falso, Guardião sem reprovação por "a definir".
