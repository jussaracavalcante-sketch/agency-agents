# 🤝 Fase 1 — Onboarding e Plano Estratégico

> **Modo**: Conta completa (Campanha usa versão reduzida) | **Duração**: 5 a 10 dias úteis | **Agentes**: 6 | **Dono humano**: Account + Supervisão de Social Media | **Gate**: G1 — plano estratégico, tom de voz, acessos, KPIs e SLAs aprovados

---

## Objetivo

Colocar o cliente em operação com **tudo que a produção precisa para não parar**: acessos, identidade, tom de voz, aprovadores, canal oficial de aprovação, KPIs e SLAs. Ao final, o Analista de Social Media consegue planejar o primeiro mês sem precisar perguntar nada básico ao cliente.

O manual de tom de voz produzido aqui é também o **insumo da IA de legendas**: sem ele, cada legenda gerada por IA exige reescrita.

## Pré-requisitos (entrada)

- [ ] Gate G0 aprovado (contrato ou aceite formal assinado)
- [ ] Pacote de handoff Account → Social recebido
- [ ] Analista de Social Media designado pela Supervisão (considerando capacidade da carteira)
- [ ] Tráfego designado, se houver mídia paga no escopo
- [ ] Reunião de kickoff agendada com o cliente

## Papéis humanos (RACI resumida)

| Atividade | Account | Supervisão de Social Media | Analista de Social Media | Tráfego | D.A./Head de Criação | Cliente |
|---|---|---|---|---|---|---|
| Kickoff com o cliente | **R/A** | C | C | C | I | C |
| Coleta de acessos | C | **A** | **R** | **R** (contas de anúncio) | I | C (concede) |
| Manual de marca e tom de voz | C | **A** | **R** | I | C (visual) | **A** (valida) |
| Aprovadores e canal oficial | **R** | C | I | I | I | **A** |
| KPIs e SLAs | **R** | C | C | C | I | **A** |
| Rastreamento e pixels | I | I | I | **R/A** | I | C |
| Plano estratégico | **A** | **R** | **R** | C | C | **A** |

## Agentes de apoio e o que pedir

> A IA organiza e rascunha. **Quem valida o manual e o plano é a Supervisão; quem aprova é o cliente.**

| Agente | Uso nesta fase | Prompt curto |
|---|---|---|
| **Brand Guardian** | Manual de marca e tom de voz | "Com base em [MATERIAIS DO CLIENTE] e [10 POSTS DE REFERÊNCIA], monte um guia de tom de voz para [CLIENTE]: personalidade, palavras que usa e evita, emojis, tratamento (você/vocês), exemplos certo/errado." |
| **Social Media Strategist** | Plano estratégico de redes | "Proponha pilares de conteúdo, mix de formatos e frequência por canal para [CLIENTE], segmento [SEGMENTO], objetivo [OBJETIVO], respeitando o escopo de [Nº PEÇAS/MÊS]." |
| **Tracking & Measurement Specialist** | Checklist de rastreamento | "Liste o que verificar em pixel Meta, API de Conversões, GA4 e Google Tag Manager para [SITE/LOJA], com prioridade e teste de validação." |
| **Account Strategist** | Mapa de stakeholders e plano de relacionamento | "Mapeie decisores, aprovadores e influenciadores de [CLIENTE] a partir de [NOTAS] e proponha ritos de relacionamento (reunião mensal, check-in)." |
| **SEO Specialist** | Diagnóstico de busca orgânica (se site/blog no escopo) | "Faça um diagnóstico rápido de SEO para [DOMÍNIO]: palavras-chave locais, perfil de empresa no Google e 5 ações prioritárias." |
| **AEO Foundations Architect** | Presença em buscadores de IA (se site no escopo) | "Verifique se [DOMÍNIO] está preparado para ser lido por buscadores de IA (llms.txt, robots, dados estruturados) e liste ações simples." |

## Passo a passo

| # | Etapa | Responsável | Sistema | Tempo típico |
|---|---|---|---|---|
| 1 | Criar cliente e projeto; abrir tarefas de onboarding | Supervisão | VJOB | 20 min |
| 2 | Reunião interna de passagem (Account → Social/Tráfego) | Account | Google Meet | 30 min |
| 3 | Kickoff com o cliente (briefing, metas, aprovadores) | Account + Analista | Google Meet | 60 a 90 min |
| 4 | Coleta de acessos (checklist abaixo) | Analista + Tráfego | Meta Business Suite, mLabs, Google Ads | 1 a 3 dias (depende do cliente) |
| 5 | Receber materiais de marca (logo, fontes, fotos, manual) | Analista | Google Drive (pasta padrão do cliente) | 1 a 3 dias |
| 6 | Rascunhar manual de tom de voz com IA | Analista | ChatGPT/Claude + Brand Guardian | 1 a 2 h |
| 7 | Revisar e validar manual internamente | Supervisão (+ Head de Criação no visual) | Google Docs | 30 a 60 min |
| 8 | Validar manual com o cliente | Account | Canal oficial de aprovação | até SLA acordado |
| 9 | Configurar/validar rastreamento | Tráfego | GTM, GA4, Meta Events Manager | 2 a 4 h |
| 10 | Montar plano estratégico (pilares, formatos, frequência, KPIs) | Analista + Supervisão | Google Docs / Canva | 3 a 5 h |
| 11 | Apresentar e aprovar plano | Account | Google Meet + registro escrito | 60 min |
| 12 | Registrar aprovadores, SLAs e canal oficial na ficha do cliente | Supervisão | VJOB (ficha do cliente) | 15 min |

### Checklist de acessos

```
Acessos do cliente
├── Meta: Business Manager com permissão de parceiro (página + Instagram + conta de anúncios + pixel)
├── TikTok / LinkedIn / YouTube (quando no escopo)
├── mLabs: perfis conectados para agendamento e relatório
├── Google: Ads, GA4, Tag Manager, Perfil da Empresa (quando no escopo)
├── Pasta compartilhada de materiais (Google Drive)
└── Contato para ofertas diárias e informações de loja
```

> Nunca solicitar senha pessoal por WhatsApp. Priorizar acesso por permissão de parceiro/gerenciador. Registrar no VJOB quem concedeu e quando.

### Manual de tom de voz — estrutura mínima (insumo para IA)

| Seção | Conteúdo |
|---|---|
| Personalidade | 3 a 5 adjetivos (ex.: próximo, confiável, direto) |
| Público | Quem é, como fala, o que valoriza |
| Tratamento | Você/vocês, formal/informal, regionalismos permitidos |
| Vocabulário | Palavras preferidas, palavras proibidas, termos técnicos do segmento |
| Emojis e hashtags | Quais usar, quantidade máxima |
| Restrições legais do segmento | Ex.: regras de publicidade de medicamentos, bebidas, promoções |
| Exemplos | 3 legendas aprovadas (certo) e 3 reprovadas (errado) com motivo |
| CTA padrão | Chamadas preferidas por objetivo (visitar loja, chamar no WhatsApp, comprar) |

### Aprovadores e canal oficial

| Item | Definição |
|---|---|
| Aprovadores autorizados | Nome do **cargo** e contato de até 2 pessoas no cliente (titular e substituto) |
| Canal oficial de aprovação | E-mail ou ferramenta com registro; WhatsApp apenas com confirmação escrita ("aprovado") |
| SLA de aprovação | Planejamento mensal e peças — meta sugerida — validar: 48 h úteis |
| Regra de silêncio | O que acontece se o prazo vencer (reagendar; nunca publicar sem aprovação) |
| Limite de rodadas | Conforme contrato (ex.: 2 rodadas) |

## Quality Gate G1

- [ ] Todos os acessos do checklist concedidos e testados
- [ ] Materiais de marca na pasta padrão do cliente
- [ ] Manual de tom de voz validado pela Supervisão e aprovado pelo cliente
- [ ] Aprovadores autorizados, substituto e canal oficial registrados no VJOB
- [ ] SLAs (aprovação, resposta, publicação) e limite de rodadas registrados
- [ ] KPIs definidos com linha de base (metas como "meta sugerida — validar")
- [ ] Rastreamento validado pelo Tráfego (quando houver mídia paga)
- [ ] Plano estratégico aprovado por escrito pelo cliente
- [ ] Ritos definidos: reunião mensal de resultados e data de fechamento do planejamento

## Riscos e como mitigar

| Risco | Dor relacionada | Mitigação |
|---|---|---|
| Cliente demora a conceder acessos | Atraso | Checklist enviado no kickoff com prazo; Account cobra no 2º dia útil |
| Aprovador não definido ou múltiplos aprovadores | Feedback fragmentado, atraso | Máximo de 2 aprovadores; demais opiniões passam pelo aprovador |
| Tom de voz vago | Retrabalho de legenda, IA genérica | Manual com exemplos certo/errado; revisão após 1º mês |
| Account passando ao Social demandas de outras áreas | Volume, desvio de escopo | Fora do escopo documentado; Supervisão valida toda demanda nova |
| Falta de conhecimento do segmento | Qualidade | Sessão de imersão com o cliente; restrições legais no manual |
| Rastreamento quebrado desde o início | Relatório sem dado | Gate só passa com rastreamento validado |

## Oportunidades de automação e IA

- **Tom de voz pré-configurado por cliente**: manual vira instrução fixa (projeto/GPT/Gem) para geração de legendas.
- **Checklist de onboarding como modelo de projeto no VJOB**, com tarefas e prazos automáticos.
- **Formulário de kickoff** que alimenta a ficha do cliente (aprovadores, SLAs, canais).
- **Alerta de acesso pendente** após 48 h (meta sugerida — validar).
- **Biblioteca de prompts por cliente** salva junto ao manual.

## Indicadores da fase

| Indicador | Meta sugerida — validar |
|---|---|
| Tempo assinatura → G1 | ≤ 10 dias úteis |
| Acessos concedidos até o 3º dia útil | ≥ 90% |
| Manual de tom de voz aprovado na 1ª rodada | ≥ 70% |
| Clientes com aprovador e canal oficial registrados | 100% |
| Clientes com KPIs e linha de base definidos | 100% |

## Handoff para a Fase 2

Use o template **Account → Social** (seção de plano aprovado) em [handoff-templates.md](../coordination/handoff-templates.md#account--social) e, se houver mídia paga, **Social → Tráfego** em [handoff-templates.md](../coordination/handoff-templates.md#social--tráfego). O pacote deve conter:

- Plano estratégico aprovado (pilares, formatos, frequência)
- Manual de marca e tom de voz
- Ficha do cliente no VJOB (aprovadores, SLAs, canal oficial, rodadas)
- KPIs e linha de base
- Datas comerciais e sazonais relevantes informadas pelo cliente

➡️ Próxima fase: [Fase 2 — Planejamento Mensal de Conteúdo](fase-2-planejamento-mensal.md)
⬅️ Fase anterior: [Fase 0 — Prospecção](fase-0-prospeccao.md)
📘 Documento-mestre: [Ciclo de Operação da Agência](../ciclo-agencia.md)

---

<sub>Adaptado do NEXUS (Network of EXperts, Unified in Strategy).</sub>
