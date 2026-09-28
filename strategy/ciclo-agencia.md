# 🔄 Ciclo de Operação da Agência

> Documento-mestre de como a agência entrega Social Media, Mídia Paga, Marca e Vendas com apoio dos 38 agentes de IA deste repositório.
> **Versão** 1.0 · **Data** 28/09/2026 · **Status** rascunho para validação da liderança · **Base** levantamento de rotinas dos setores de Social Media (incluindo SAC e analistas multifunção) e Mídia Paga (09/2026) + identidade pública da agência

---

## 1. Resumo executivo

A agência vende **resultado comercial** ("ajudar as empresas a vender mais através do marketing e tecnologia"). A operação que entrega esse resultado é recorrente: **planejar → produzir → aprovar → publicar → medir → replanejar**, todo mês e para cada cliente, com picos de campanha no meio.

O levantamento das rotinas do setor de Social Media mostra que o trabalho é bem executado, mas **perde tempo nas passagens entre pessoas**:

| Dor declarada pelo time | Prioridade | Onde o Ciclo resolve |
|---|---|---|
| Atraso por dependência de aprovação do cliente | Alta | [Fase 4](playbooks/fase-4-aprovacao.md): janela de retorno, lembrete e escalonamento |
| Briefing incompleto gera retrabalho | Alta | [Fase 3](playbooks/fase-3-producao.md): briefing com campos obrigatórios |
| Volume simultâneo de demandas | Alta | [Fase 2](playbooks/fase-2-planejamento-mensal.md): calendário fechado antes do mês; filtro de extras |
| Feedback espalhado em vários canais | Média | [Handoff Cliente→Social](coordination/handoff-templates.md): um registro por peça |
| Demandas de outras áreas chegando ao Social | Média | [Handoff Account→Social](coordination/handoff-templates.md): triagem planejado × extra |
| Publicação e conferência manuais | Média | [Fase 5](playbooks/fase-5-publicacao-e-midia.md): checklist e agendamento |
| IA usada caso a caso, sem padrão | Média | [Biblioteca de prompts](coordination/agent-activation-prompts.md) |
| Relatórios montados à mão | Média | [Fase 6](playbooks/fase-6-resultados.md): coleta automática + análise por IA |
| Mídia: criativo aprovado chega em cima do lançamento | Alta | [Fase 3](playbooks/fase-3-producao.md) + Paid Social Strategist: data-limite de criativo por campanha |
| Mídia: supervisão absorve execução e perde tempo de estratégia | Alta | Paid Media Auditor na revisão técnica; delegação da execução ao Analista |
| Mídia: mudança de verba pedida só por WhatsApp | Média | Regra: alteração de verba só vale por e-mail ou chamado no VJOB |
| Mídia: conferência manual de saldo, UTM e tags | Média | Alertas de saldo a 90% e script de auditoria de UTM/tags (Tracking & Measurement Specialist) |
| Esquecimento de datas importantes | Alta | [Fase 2](playbooks/fase-2-planejamento-mensal.md): calendário anual por conta com alertas |
| Urgências interrompem o planejado | Alta | [Fase 2](playbooks/fase-2-planejamento-mensal.md): níveis P1–P3 e janela diária reservada para urgências |
| Conteúdo técnico sem validador definido (saúde e outros regulados) | Alta | [Fase 3](playbooks/fase-3-producao.md): validador técnico obrigatório no briefing |
| SAC: respostas diferentes na mesma conta e informação de campanha desatualizada | Média | [Fase 5](playbooks/fase-5-publicacao-e-midia.md): ficha da marca única e banco de respostas |
| Acervo de fotos e vídeos difícil de reaproveitar | Média | [Fase 3](playbooks/fase-3-producao.md): padrão de pastas e nomes de arquivo |

**Princípio central:** os agentes de IA preparam, sugerem e revisam; **pessoas decidem, aprovam e publicam**. Nenhuma peça vai ao ar sem aprovação escrita do cliente.

---

## 2. Quem somos (identidade pública)

Informações públicas do site institucional, LinkedIn e imprensa regional (consulta em 28/09/2026). Números com divergência entre fontes estão sinalizados.

| Item | Conteúdo |
|---|---|
| Posicionamento | "Maior Martech do Norte do país" · "A agência estratégica que conecta o Norte ao crescimento nacional" · "Não é apenas uma agência de marketing; somos uma consultoria com foco em execução martech" |
| Missão | Ajudar as empresas a vender mais através do marketing e tecnologia |
| Visão | Obter 500 clientes recorrentes no Brasil até 2030 |
| Valores | Integridade, Respeito, Honestidade, Comprometimento, Disciplina, Humildade e Resiliência |
| Origem | Fundada em 2006 como agência de comunicação; marketing digital desde 2012; hoje martech 360º |
| Sedes | Manaus/AM e São Paulo/SP; atuação declarada em até 10 estados *(fontes divergem: 7 + DF ou 10)* |
| Escala | "+100 colaboradores" e "+100 clientes ativos" *(autodeclarado)* |
| Serviços | Redes sociais · Mídia performance (Google, Meta, TikTok, LinkedIn, Waze, X) · Inbound e automação · SEO · E-commerce · Desenvolvimento web · BI e CRO · Mídia offline · CRM/RevOps · In Company · VBOT (atendimento e vendas via WhatsApp) |
| Credenciais | Parceira RD Station *(nível Diamond ou Platinum: fontes divergem, confirmar)*; Google Partner e Meta citados na imprensa; SGQ ISO 9001:2015 (informação interna, sem divulgação pública) |
| Tom de voz | Assertivo, orientado a vendas, técnico (CAC/LTV, RevOps, IA), com prova social ("a maior do Norte", "+100 clientes") |

> **Implicação para o Ciclo:** todo conteúdo e todo relatório precisa ligar a entrega a **venda, lead ou receita** do cliente, e não só a curtidas. Isso orienta os KPIs da [Fase 6](playbooks/fase-6-resultados.md).

---

## 3. O Ciclo em uma página

```
                 ┌──────────────── CONTA NOVA ────────────────┐
                 │                                            │
   FASE 0 ──► FASE 1 ──► ┌───────────── CICLO MENSAL (recorrente) ─────────────┐
 Prospecção   Onboarding │                                                     │
 Diagnóstico  Plano      │  FASE 2 ──► FASE 3 ──► FASE 4 ──► FASE 5 ──► FASE 6 │
 Proposta     Estratégico│ Planejar    Produzir   Aprovar    Publicar   Medir  │
                         │    ▲                                           │    │
                         │    └──────── plano de ação do mês seguinte ────┘    │
                         └─────────────────────────────────────────────────────┘
                                   ▲ campanhas sazonais entram na Fase 2
                                   ▲ crises e atrasos → runbook de crise
```

| Fase | Nome | Dono humano | Saída que fecha a fase (gate) | Playbook |
|---|---|---|---|---|
| 0 | Prospecção, diagnóstico e proposta | Comercial / Account | Proposta aceita e escopo assinado | [fase-0](playbooks/fase-0-prospeccao.md) |
| 1 | Onboarding e plano estratégico | Account + Supervisão de Social | Plano, tom de voz, acessos, aprovadores, KPIs e SLAs aprovados | [fase-1](playbooks/fase-1-onboarding.md) |
| 2 | Planejamento mensal de conteúdo | Analista de Social | Calendário e pautas aprovados **antes** do mês começar | [fase-2](playbooks/fase-2-planejamento-mensal.md) |
| 3 | Produção criativa | Analista de Social + Criação (D.A.) | Peças revisadas no checklist interno | [fase-3](playbooks/fase-3-producao.md) |
| 4 | Aprovação e controle de qualidade | Analista + Supervisão · **Cliente aprova** | Aprovação escrita e registrada | [fase-4](playbooks/fase-4-aprovacao.md) |
| 5 | Publicação, comunidade e mídia paga | Analista de Social · SAC · Tráfego | Publicado no dia e hora, check no VJOB, interações respondidas | [fase-5](playbooks/fase-5-publicacao-e-midia.md) |
| 6 | Mensuração, relatório e otimização | Analista · Supervisão · Account | Relatório, reunião de resultados e plano de ação | [fase-6](playbooks/fase-6-resultados.md) |

---

## 4. Papéis humanos e responsabilidades

Papéis descritos a partir das rotinas levantadas. O documento não identifica pessoas; a alocação nominal fica no VJOB e no organograma interno.

| Papel | Responsabilidade no Ciclo | Decide sozinho | Precisa de autorização |
|---|---|---|---|
| **Account** | Porta de entrada do cliente; alinha expectativas, campanhas e escopo; valida planejamento e relatório com o cliente | Encaminhamento da demanda à área certa | Mudança de escopo, custo adicional |
| **Supervisão de Social Media** | Prioriza a fila, conduz a daily, monitora prazos e atrasos, garante qualidade e aderência ao plano, gere carteira e capacidade (Sede, House, SAC), faz 1:1 e check-in semanais, reporta à Diretoria de Operações | Prioridades, redistribuição de analistas, encaminhamentos operacionais | Contratação, custo, mudança estrutural de escopo ou equipe, validação visual crítica (Head de Criação) |
| **Analista de Social Media** | Planeja o mês, escreve pautas e legendas, faz o briefing ao D.A., acompanha a peça, envia para aprovação, agenda e publica, responde à comunidade, mede e faz o relatório de conta; roteiriza, capta e edita quando aplicável. Em algumas contas o papel é **multifunção** (Social + direção de arte + audiovisual), inclusive cobertura de eventos e comunicação interna do cliente; em carteiras **multimarca** alterna tom de voz por marca | Texto de legenda, horário de postagem, resposta ao público, sequência de Stories, formato sugerido | Publicar fora do planejado, mudar identidade ou oferta, qualquer peça sem aprovação do cliente |
| **Criação (D.A. / designers)** | Produz e ajusta peças a partir do briefing | Execução visual dentro do briefing | Desvio de identidade visual |
| **Head de Criação** | Valida qualidade visual quando acionado | Padrão visual | — |
| **Redação / Audiovisual** | Texto, roteiro, captação e edição quando não feitos pelo Social | Execução técnica | — |
| **Supervisão de Mídia Paga** | Prioriza a fila do time, conduz a daily, revisa tecnicamente toda campanha antes de ativar, audita rastreamento, controla atrasos no VJOB, valida relatórios, gere carteira por complexidade (e-commerce × leads), faz 1:1 e check-in semanais, defende verba com Account e cliente | Otimizações e reestruturações de campanha, redistribuição de contas entre analistas (com justificativa à Diretoria) | Verba fora do contrato, contratação, descontos ou ressarcimentos, mudança estrutural do setor |
| **Analista de Mídia Paga** | Checa saldo e ritmo de verba, sobe e otimiza campanhas (Meta, Google, TikTok), implementa pixel/CAPI/GTM/GA4, atende dúvidas técnicas do Account, faz o relatório mensal para validação | Pausar peças fracas, redistribuir verba diária dentro do total aprovado, testar públicos e formatos | Mudar a verba total, criar estrutura fora do escopo, enviar relatório ao cliente sem validação |
| **Analista de SAC (redes sociais)** | Monitora comentários e directs ao longo do dia, classifica (elogio, dúvida, reclamação, caso sensível), responde com a ficha da marca, leva reclamações ao privado, repassa ao cliente o que exige apuração, mantém o banco de respostas; apoia o time inserindo o planejamento no iClips | Redação da resposta dentro da ficha da marca, quando levar ao privado, ajuste de tom ao contexto | Informação comercial não confirmada, posicionamento em caso sensível, pós-venda que exige apuração |
| **Fast Mídia** | Demandas rápidas de conteúdo e publicação | Execução dentro do padrão | Qualquer peça sem aprovação |
| **Diretoria de Operações** | Valida capacidade, realocações, casos graves, relatório de operação | Estrutura da operação | — |
| **Cliente** | Fornece briefing, ofertas e materiais; **aprova por escrito** | Aprovação final | — |

---

## 5. Agentes de IA por fase

Os 38 agentes ativos estão em [`brand/`](../brand/), [`marketing/`](../marketing/), [`paid-media/`](../paid-media/) e [`sales/`](../sales/). Prompts prontos em [agent-activation-prompts.md](coordination/agent-activation-prompts.md).

| Fase | Agentes principais | Agentes sob demanda |
|---|---|---|
| 0 | Outbound Strategist · Discovery Coach · Proposal Strategist · Paid Media Auditor | Offer & Lead Gen Strategist · Deal Strategist · Pipeline Analyst · Social Media Strategist (auditoria de redes) |
| 1 | Brand Guardian · Social Media Strategist · Tracking & Measurement Specialist | Account Strategist · SEO Specialist · AEO Foundations Architect |
| 2 | Social Media Strategist · Content Creator · Instagram Curator | TikTok Strategist · LinkedIn Content Creator · Growth Hacker · Email Marketing Strategist · Podcast Strategist |
| 3 | Content Creator · Visual Storyteller · Image Prompt Engineer · Short-Video Editing Coach | Carousel Growth Engine · Ad Creative Strategist · Brand Guardian |
| 4 | Brand Guardian · Ad Creative Strategist (políticas de anúncio) | PR & Communications Manager (temas sensíveis) |
| 5 | Instagram Curator · Paid Social Strategist · PPC Campaign Strategist · Tracking & Measurement Specialist | TikTok Strategist · Twitter Engager · Video Optimization Specialist · Programmatic & Display Buyer · Reddit Community Builder |
| 6 | Social Media Strategist · Paid Media Auditor · Account Strategist | Search Query Analyst · X/Twitter Intelligence Analyst · AI Citation Strategist · Agentic Search Optimizer · Pipeline Analyst |

**Regras de uso de IA**
1. A IA gera a **primeira versão**; o humano do papel responsável revisa antes de enviar ao cliente ou publicar.
2. Nunca inserir em prompts: senhas, dados pessoais de consumidores finais, dados financeiros do cliente não autorizados.
3. Imagem gerada por IA segue direitos de imagem, identidade da marca e políticas das plataformas; pessoa real só com autorização.
4. Cada cliente tem **tom de voz documentado** (Fase 1), usado como contexto fixo nos prompts de legenda e roteiro.

---

## 6. Modos de ativação

| Modo | Quando usar | Fases | Duração típica | Runbook |
|---|---|---|---|---|
| **Conta completa** | Cliente novo ou reestruturação de conta | 0 → 6, depois ciclo mensal | 2–3 semanas até o 1º calendário | [Onboarding](runbooks/cenario-onboarding-cliente.md) · [Rotina mensal](runbooks/cenario-rotina-mensal-social.md) |
| **Campanha** | Data comemorativa, ação de loja, lançamento, influenciadores | 2 → 6 concentradas | 2–6 semanas | [Campanha sazonal](runbooks/cenario-campanha-sazonal.md) · [Auditoria de mídia](runbooks/cenario-auditoria-midia-paga.md) |
| **Demanda pontual** | Extra aprovado, auditoria, crise, atraso crítico | Fase específica | Horas a dias | [Crise e atraso](runbooks/cenario-crise-e-atraso.md) |

> No `runbooks.json` esses modos aparecem como `NEXUS-Full`, `NEXUS-Sprint` e `NEXUS-Micro` por compatibilidade com o app do catálogo.

---

## 7. Ritos da operação

| Rito | Frequência | Dono | Duração | Entrada → Saída | Sistema |
|---|---|---|---|---|---|
| Triagem e priorização | Diária, início do dia | Supervisão; Analista na própria fila | 15–30 min | WhatsApp, e-mail, VJOB, pendências → fila priorizada | VJOB, Dash, Gmail |
| Daily | Diária | Supervisão | 30–40 min | Status e impedimentos → prioridades e redistribuição | Google Meet |
| Check de atrasos e pontualidade | Diária | Supervisão / Analista | 15–30 min | VJOB → cobranças e escalonamentos | VJOB |
| Check de publicação | Diária | Analista | 30 min | Agenda do dia → check no VJOB | VJOB, mLabs, Meta |
| Checagem de saldo e ritmo de verba | Diária | Analista e Supervisão de Mídia Paga | 45–60 min *(meta: alerta automático a 90% do orçamento)* | Gerenciadores → contas sem risco de pausa ou estouro | Meta Ads, Google Ads, TikTok Ads |
| Revisão técnica de campanha | A cada subida | Supervisão de Mídia Paga | até 1h30/dia | Setup do analista → liberação ou correção | Gerenciadores, GTM, GA4 |
| Check-in semanal de resultados | Semanal | Supervisão | 30–60 min | Entregas, indicadores, gargalos → plano de ação | Dash, VJOB |
| 1:1 com analistas | Semanal | Supervisão | até 1 h cada | Rotina, carga, desenvolvimento → registro | Qulture |
| Planejamento mensal | Mensal, antes do ciclo | Analista (valida Supervisão/Account/Cliente) | até 1 dia por cliente *(meta: reduzir com IA)* | Estratégia + datas → calendário e pautas | Planilhas, iClips |
| Reunião de resultados | Mensal | Account + Analista | 30–60 min | Relatório → próximos passos | Meet / presencial |
| Relatório de operação | Mensal | Supervisão → Diretoria de Operações | 2–4 h *(meta: automatizar)* | VJOB, Dash → relatório executivo | Dash, planilhas |
| Auditoria de redes e processos | 1–2x por mês | Supervisão | variável | Perfis e execução → plano de melhorias | Mlabs, Instagram |
| Revisão de carteira e capacidade | 1–2x por mês | Supervisão + Diretoria de Operações | variável | Volume, escopo, entradas e saídas → realocações | VJOB, planilhas |

---

## 8. Sistemas e fonte da verdade

| Sistema | Papel no Ciclo | Regra |
|---|---|---|
| **VJOB** | Tarefas, prazos, atrasos, carteira | **Fonte da verdade** de status e prazo. Demanda fora do VJOB não existe para a operação |
| **iClips** | Jobs, cards de peça, alterações, fluxo de produção | Todo ajuste de peça é registrado no card, não só no WhatsApp |
| **WhatsApp / Google Chat** | Comunicação rápida com cliente e equipe | Canal de conversa, não de registro. Aprovação recebida aqui é copiada para o card |
| **Gmail** | Comunicação formal e registro | Canal preferencial para aprovação formal e escopo |
| **mLabs / Meta Business Suite** | Agendamento, publicação, métricas | Só agenda peça com aprovação registrada |
| **Dash / planilhas** | Indicadores de operação e de conta | Alimentam check-in, relatório e auditoria |
| **Qulture** | Registro de 1:1 e desenvolvimento | Uso da Supervisão |
| **Canva, CapCut** | Edição rápida | Arquivos finais versionados no job |
| **IA generativa** | Texto, roteiro, imagem, análise | Ver regras da seção 5 |

---

## 9. Quality gates (resumo)

| Gate | Pergunta de passagem | Quem assina |
|---|---|---|
| G0 | O escopo tem nº de peças por mês, canais, SLA de aprovação e limite de rodadas? | Comercial + Account |
| G1 | Tom de voz, acessos, aprovadores autorizados, canal de aprovação e KPIs estão documentados? | Account + Supervisão |
| G2 | O calendário do mês foi aprovado antes do dia 1º e cada pauta tem todos os campos? | Supervisão (Cliente aprova) |
| G3 | A peça passou no checklist interno (marca, texto, oferta, formato, política)? | Analista (Head de Criação quando acionado) |
| G4 | Existe aprovação escrita, do aprovador autorizado, registrada no card? | Analista + Supervisão |
| G5 | Publicou no dia e hora, com check no VJOB e rastreamento (UTM) quando há mídia? | Analista / Tráfego |
| G6 | O relatório liga resultado a objetivo comercial e gera plano de ação para o próximo mês? | Account + Supervisão |

Detalhe dos checklists em cada playbook. Para mídia paga, a aprovação segue o POP do SGQ **VAN-POP-MKT-001 — Aprovação de Criativos de Mídia Paga** (rascunho em aprovação).

---

## 10. Indicadores do Ciclo

Metas sugeridas para validação da Diretoria de Operações após 1 mês de medição de base.

| Indicador | Fórmula | Meta sugerida — validar | Fonte |
|---|---|---|---|
| Entregas no prazo | atividades concluídas no prazo ÷ atividades do período | ≥ 90% | VJOB |
| Calendário aprovado antes do mês | clientes com calendário aprovado até D-3 ÷ clientes ativos | ≥ 95% | VJOB / iClips |
| Aprovação na 1ª rodada | peças aprovadas sem ajuste ÷ peças enviadas | ≥ 70% | iClips |
| Tempo médio de retorno do cliente | média (data aprovação − data envio) | ≤ 2 dias úteis | iClips |
| Retrabalho por briefing incompleto | ajustes com causa "falta de informação" ÷ ajustes | ≤ 10% | iClips |
| Demandas extras | extras aprovadas ÷ demandas totais | monitorar; acima de 20% revisar escopo | VJOB |
| Cumprimento do planejamento | publicações realizadas ÷ planejadas | ≥ 95% | mLabs / VJOB |
| Volume por analista | atividades ativas por analista | faixa definida pela Supervisão | VJOB |
| Resultado de conta | KPI comercial do cliente (leads, vendas, tráfego ao site, conversas no WhatsApp) | definido no onboarding | Relatório de conta |

> Enquanto o saneamento de prazos do VJOB não terminar, o contador de atraso da base **não deve ser usado como KPI oficial**. Use a medição por amostra da Supervisão.

---

## 11. Roadmap de automação e IA

Prioridades a partir das sugestões do próprio time. Estimativas de ganho vêm dos levantamentos e precisam ser medidas.

| # | Automação | Dor que resolve | Tempo hoje (levantamento) | Fase |
|---|---|---|---|---|
| 1 | Alertas automáticos de prazo e atraso por responsável | Atrasos | 15–60 min/dia por pessoa | Transversal |
| 2 | Fluxo de aprovação com status, lembrete e histórico | Aprovação e feedback espalhado | até 2 h/dia por analista | 4 |
| 3 | Agente que transforma pedido em briefing padronizado | Briefing incompleto | ≈ 1 h/dia por analista | 3 |
| 4 | Legendas com tom de voz pré-configurado por cliente | Tempo de redação | 15 min/dia | 3 |
| 5 | Calendário com sugestão de datas e pautas | Planejamento manual | até 1 dia por cliente/mês | 2 |
| 6 | 1ª versão de roteiro de Reels por IA | Roteirização | 30–90 min por roteiro | 3 |
| 7 | Coleta automática de métricas + relatório com insights | Relatórios manuais | 2–4 h/mês (Supervisão); 1–2 h por relatório | 6 |
| 8 | Checklist de publicação automatizado | Conferência manual | 30 min/dia | 5 |
| 9 | Biblioteca de prompts por atividade | IA caso a caso | — | Transversal |
| 10 | Classificação de comentários e alerta de caso sensível no SAC | Demora em achar reclamação crítica | contínuo | 5 |
| 11 | Calendário anual com alertas de datas por conta | Datas esquecidas | recorrente | 2 |
| 12 | Resumo de feedback do cliente em checklist de ajustes | Retrabalho por feedback fragmentado | recorrente | 4 |

---

## 12. Riscos do Ciclo

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Cliente não aprova no prazo e a data passa | Alta | Alto | Janela de retorno no escopo (G0), lembrete automático, escalonamento via Account |
| Publicação sem aprovação registrada | Média | Alto | G4 obrigatório; mLabs só com card aprovado |
| Informação comercial errada (preço, validade, oferta) | Média | Alto | Checklist G3 com conferência de oferta; aprovação do responsável comercial do cliente |
| Sobrecarga de analista por extras | Alta | Médio | Filtro de extras (Account + Supervisão) e revisão de carteira |
| Dependência de uma pessoa por conta | Média | Médio | Tom de voz e histórico documentados; cobertura cruzada nos recessos |
| Uso indevido de IA (imagem, dado pessoal) | Baixa | Alto | Regras da seção 5; revisão humana obrigatória |
| Números públicos da agência inconsistentes | Média | Baixo | Padronizar anos de mercado, estados e nº de clientes na comunicação institucional |

---

## 13. Como começar

1. Leia o [EXECUTIVE-BRIEF](EXECUTIVE-BRIEF.md) (1 página) e o [QUICKSTART](QUICKSTART.md) (5 minutos).
2. Escolha o runbook do seu cenário em [`runbooks/`](runbooks/).
3. Use os [modelos de passagem](coordination/handoff-templates.md) e os [prompts de ativação](coordination/agent-activation-prompts.md).

---

<sub>Adaptado do método NEXUS do projeto de origem (agency-agents), reescrito para a operação de agência. Sem dados pessoais de colaboradores ou clientes, porque o repositório é público.</sub>
