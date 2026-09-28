# Base de Conhecimento — Vanguarda Martech

> Contexto obrigatório para todo agente deste repositório que atue para a Vanguarda Martech.
> Leia este arquivo antes de produzir qualquer entrega. Última consolidação: 28/09/2026.

---

## 1. Quem é o cliente interno

**Vanguarda Martech** é uma agência de **martech, mídia paga, dados e inteligência artificial**
sediada em **Manaus/AM (fuso UTC−4, sem horário de verão)**. Integra um ecossistema com:

| Empresa | Papel no ecossistema |
|---|---|
| **Vanguarda Martech** | Mídia paga, dados, automação de marketing e IA |
| **Vanguarda Comunicação** | Comunicação, conteúdo e relacionamento com marcas |
| **VPromo** | Promoções e ativações |
| **VBOT** | Automação conversacional / bots |

- **SGQ certificado ISO 9001:2015.** Todo procedimento recorrente é formalizado como **POP**
  (Procedimento Operacional Padrão). Se a entrega descreve um processo repetível, proponha o POP.
- A área de **IA** reporta à presidência e conduz a frente de dados e IA da casa.

## 2. Portfólio de serviços (onde cada agente se encaixa)

| Serviço da Vanguarda | Agentes principais |
|---|---|
| Mídia paga Google Ads (Search, PMax, Display, YouTube) | `ppc-campaign-strategist`, `search-query-analyst`, `paid-media-auditor`, `programmatic-display-buyer` |
| Mídia paga META Ads (Facebook/Instagram) e TikTok Ads | `paid-social-strategist`, `ad-creative-strategist` |
| Rastreamento e mensuração (GA4, GTM, pixel, CAPI, conversões offline) | `tracking-measurement-specialist`, `analytics-reporter` |
| Inbound, CRM e automação (RD Station, e-mail) | `email-marketing-strategist`, `growth-hacker`, `automation-governance-architect` |
| SEO, AEO e visibilidade em IA generativa | `seo-specialist`, `aeo-foundations-architect`, `ai-citation-strategist`, `agentic-search-optimizer` |
| Conteúdo e redes sociais | `social-media-strategist`, `content-creator`, `instagram-curator`, `tiktok-strategist`, `linkedin-content-creator`, `carousel-growth-engine`, `multi-platform-publisher`, `short-video-editing-coach`, `video-optimization-specialist` |
| Marca, criação e imagem | `brand-guardian`, `visual-storyteller`, `image-prompt-engineer` |
| Assessoria e reputação | `pr-communications-manager` |
| E-commerce e marketplaces | `cross-border-e-commerce-specialist`, `app-store-optimizer` |
| Novos negócios e propostas comerciais | `proposal-strategist`, `offer-lead-gen-strategist`, `outbound-strategist`, `discovery-coach`, `deal-strategist`, `account-strategist`, `pipeline-analyst` |
| Inteligência de mercado e voz do cliente | `trend-researcher`, `feedback-synthesizer`, `x-twitter-intelligence-analyst` |
| Relatórios para clientes e diretoria | `analytics-reporter`, `report-distribution-agent` |
| LGPD e governança de dados | `data-privacy-officer`, `automation-governance-architect` |

**Demais divisões instaladas** (apoio às frentes internas de IA, dados, PMO e SGQ):

| Frente da Vanguarda | Divisões / agentes úteis |
|---|---|
| Projeto VanguardIA e produtos de IA | `engineering` (ex.: `ai-engineer`, `backend-architect`, `frontend-developer`), `product-manager`, `mcp-builder` |
| Dados (Nekt, dashboards) | `data-engineer`, `data-visualization-engineer`, `data-consolidation-agent` |
| PMO, VJOB e governança | `project-management` (ex.: `project-shepherd`, `senior-project-manager`), `workflow-architect`, `operations-manager` |
| SGQ ISO 9001 e POPs | `document-generator`, `workflow-architect`, `testing` |
| Lei do Bem e editais | `grant-writer`, `finance` |
| Segurança e LGPD | `security`, `data-privacy-officer`, `legal-document-review` |
| Treinamento interno | `corporate-training-designer`, `change-management-consultant` |

Agentes voltados a mercados ou setores fora do portfólio (China, games, saúde, GIS etc.) continuam
instalados, mas só devem ser usados quando houver cliente ou demanda correspondente.

**Orquestração sugerida:** para uma campanha completa, encadeie
`trend-researcher` → `social-media-strategist` / `ppc-campaign-strategist` → `ad-creative-strategist`
→ `tracking-measurement-specialist` → `analytics-reporter`.

## 3. Carteira de clientes (perfil)

- A agência opera uma **MCC do Google Ads com dezenas de contas de clientes** (~88), com forte presença
  de **varejo regional do Norte** — concessionárias e grupos automotivos (veículos, motos, consórcio,
  pós-venda), redes de varejo com lojas físicas e e-commerce, pneus, farmácias, clínicas de estética e
  saúde, relojoaria.
- **Vários clientes são grupos multi-conta** (uma marca com contas separadas por unidade, cidade ou
  linha de negócio). **O nome do cliente é ambíguo: sempre confirmar qual conta/ID antes de analisar
  ou recomendar.**
- Praças relevantes: **Manaus/AM e Porto Velho/RO**, além de campanhas nacionais para e-commerce.

## 4. Stack e ferramentas disponíveis

| Ferramenta | Uso |
|---|---|
| **Google Ads (MCC)** | Métricas de campanha, palavras-chave, termos de busca, anúncios, GAQL |
| **META Ads** | Mídia paga social |
| **Semrush** | SEO, concorrência, palavras-chave, tráfego |
| **Nekt** | Nova arquitetura de dados institucional (data lake / camada semântica) |
| **RD Station** | Inbound, automação e CRM (integração ao Nekt em andamento) |
| **TESS AI** | IA generativa corporativa, consolidadora do stack de software |
| **VJOB** | Sistema corporativo de tarefas e prazos |
| **Jira / Notion** | Backlog de produto de IA e Central de PMO |
| **Power BI / Looker Studio** | Dashboards para clientes e diretoria |

Quando houver conector ativo (Google Ads, Semrush, Nekt), **o dado vem da ferramenta, não de suposição.**

## 5. Regras inegociáveis para todos os agentes

1. **Idioma: português do Brasil.** Moeda em **R$** (formato `R$ 1.234,56`), datas em **DD/MM/AAAA**,
   números com separador de milhar `.` e decimal `,`.
2. **Nunca inventar número, benchmark, resultado ou papel.** Dado ausente vai para a seção
   *Ressalvas* ou vira pergunta. Benchmarks de mercado devem citar fonte e ano.
3. **Confirmar a conta/cliente** antes de qualquer análise de mídia.
4. **LGPD (Lei 13.709/2018):** não replicar dados pessoais de leads/clientes finais em relatórios;
   agregar, anonimizar e citar apenas o necessário. Base legal e consentimento para remarketing,
   listas de clientes e CAPI devem ser verificados.
5. **Publicidade no Brasil:** respeitar o **CONAR** e o **CDC**; em saúde/estética seguir regras do
   **CFM/CFO/ANVISA** (sem promessa de resultado, sem antes/depois indevido); em automotivo e
   consórcio, informar condições de oferta (preço, taxa, prazo, validade) conforme exigência legal.
6. **Indicadores formalmente invalidados pela casa não são usados como KPI** (ex.: contador de atraso
   do VJOB enquanto o saneamento de prazos não for concluído).
7. **Custo explícito:** toda proposta que consome verba, licença ou crédito de API declara o custo em R$.
8. **Não expor ativos ou dados de um cliente em entrega de outro.**

## 6. Padrão de entrega

Entregas executivas, nível consultoria (Big Four / McKinsey), sem enrolação. Estrutura padrão:

1. **Resumo Executivo** (3–5 linhas, com a recomendação)
2. **Diagnóstico** (com evidência numérica e fonte)
3. **Análise** (causa-raiz, benchmark quando houver fonte)
4. **Riscos** e **Oportunidades**
5. **Plano de Ação** — 5W2H ou tabela com *ação · dono · prazo · KPI*
6. **Cronograma** e, quando couber, **RACI**
7. **KPIs / OKRs** de acompanhamento
8. **Ressalvas** (o que a fonte não permitiu afirmar)
9. **Próximos Passos**

Formatos: **1-pager HTML** como padrão interno; **.docx** para cliente externo, conselho ou ata;
**POP** para procedimento do SGQ. Relatórios de mídia devem trazer, no mínimo: investimento, impressões,
cliques, CTR, CPC, conversões, CPA/CPL, taxa de conversão e ROAS (quando houver receita rastreada),
comparando com o período anterior.

## 7. Glossário interno

| Sigla / termo | Significado |
|---|---|
| **MCC** | Conta administradora do Google Ads com as contas dos clientes |
| **POP** | Procedimento Operacional Padrão do SGQ |
| **SGQ** | Sistema de Gestão da Qualidade (ISO 9001:2015) |
| **VJOB** | Sistema corporativo de tarefas e prazos |
| **VanguardIA / Vgda.IA** | Projeto de IA próprio da casa |
| **Nekt** | Plataforma da nova arquitetura de dados |
| **TESS AI** | Plataforma de IA generativa corporativa |
| **Lei do Bem** | Incentivo fiscal de P&D (Lei 11.196/2005) aplicado aos projetos de IA |
| **Demo Day IA FIRST** | Ritual interno de apresentação de casos reais de IA |

## 8. Manutenção

Atualize este arquivo quando mudar serviço, ferramenta, regra ou perfil de carteira.
Após atualizar, **não é preciso reinstalar**: os agentes leem este arquivo em tempo de execução.
Para reinstalar/atualizar os agentes: veja [`README.md`](README.md).
