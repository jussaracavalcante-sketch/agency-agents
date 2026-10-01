# 🤝 Runbook: Onboarding de Novo Cliente

> **Modo**: Conta completa (NEXUS-Full) | **Duração**: 2–3 semanas (sugerida) | **Agentes**: 8–11

---

## Cenário

O contrato foi assinado (Gate G0 da [Fase 0](../playbooks/fase-0-prospeccao.md) concluído). O cliente ainda não tem calendário, tom de voz documentado nem acessos entregues. O objetivo é sair do contrato assinado para o **1º calendário editorial aprovado**, com acessos, aprovadores, SLAs e linha de base de desempenho definidos.

Este runbook cobre a [Fase 1 — Onboarding e Plano Estratégico](../playbooks/fase-1-onboarding.md) e a primeira execução da [Fase 2 — Planejamento Mensal](../playbooks/fase-2-planejamento-mensal.md).

**Regra de ouro:** agentes de IA preparam rascunhos, diagnósticos e checklists. Quem decide, aprova e fala com o cliente é sempre um humano.

## Roster de agentes

### Núcleo
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Account Strategist | Mapa de stakeholders do cliente, expectativas, pauta do kickoff | Account |
| Brand Guardian | Rascunho do guia de tom de voz e identidade a partir de materiais do cliente | Account + Supervisão de Social Media |
| Social Media Strategist | Auditoria inicial das redes e proposta de linhas editoriais | Supervisão de Social Media |
| Paid Media Auditor | Auditoria inicial das contas de mídia paga (se houver no escopo) | Tráfego (Mídia Paga) |
| Tracking & Measurement Specialist | Checklist de rastreamento: pixel, conversões, GA4, UTMs | Tráfego (Mídia Paga) |

### Especialistas
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Content Creator | Rascunho das primeiras pautas e legendas-modelo no tom aprovado | Analista de Social Media |
| Instagram Curator | Diagnóstico de perfil, grade e formatos prioritários | Analista de Social Media |
| SEO Specialist | Diagnóstico rápido de busca orgânica e perfil de empresa (se no escopo) | Account |
| AEO Foundations Architect | Verificação de presença do site para buscadores com IA (se no escopo) | Account |

### Apoio
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| TikTok Strategist | Diagnóstico de vídeo curto, se o canal estiver no escopo | Analista de Social Media |
| Growth Hacker | Hipóteses de crescimento para os 90 primeiros dias | Supervisão de Social Media |

## Plano de execução

### Semana 1: Kickoff, acessos e tom de voz

```
Dia 1: Passagem de bastão interna
├── Account → registra o escopo assinado no VJOB (projeto do cliente)
│   ├── Canais, volume mensal de peças, mídia paga sim/não, verba
│   └── Handoff Account→Social (../coordination/handoff-templates.md)
├── Supervisão de Social Media → define Analista responsável e checa capacidade da carteira
└── Account Strategist (apoia) → mapa de stakeholders e pauta do kickoff

Dia 2–3: Kickoff com o cliente (Google Meet, 60–90 min)
├── Account conduz · Supervisão e Analista participam
├── Pauta: objetivos, público, praças, concorrentes, datas-chave do ano
├── Definir APROVADORES AUTORIZADOS (quem aprova peça, oferta e verba)
├── Definir canal oficial de aprovação (e-mail ou registro rastreável; POP VAN-POP-MKT-001)
└── Solicitar materiais: manual de marca, fotos, logos, tabela de ofertas

Dia 3–5: Acessos e tom de voz
├── Analista → checklist de acessos
│   ├── Meta Business Suite (perfil comercial, página, conta de anúncios)
│   ├── mLabs (agendamento) · Google Ads / GA4 (se mídia paga)
│   └── Pasta compartilhada de materiais
├── Brand Guardian (apoia) → rascunho do guia de tom de voz
│   ├── Palavras que usamos / evitamos, emojis, tratamento
│   └── Exemplos de legenda "certo / errado"
└── Account → envia o rascunho do tom de voz para validação do cliente
```

### Semana 2: Auditoria inicial, KPIs e SLAs

```
Dia 6–7: Auditoria de redes e mídia
├── Social Media Strategist (apoia) → auditoria de redes
│   ├── Frequência, formatos, engajamento, respostas a comentários
│   └── Benchmark de 3 concorrentes da praça
├── Instagram Curator (apoia) → grade, destaques, bio, CTA
├── Paid Media Auditor (apoia) → estrutura de contas, verba, conversões
├── Tracking & Measurement Specialist (apoia) → pixel, eventos, UTMs
└── Supervisão + Tráfego → revisam achados e priorizam

Dia 8–9: Plano estratégico
├── Supervisão consolida: linhas editoriais, canais, frequência
├── Growth Hacker (apoia) → hipóteses dos 90 primeiros dias
├── Account + Supervisão → KPIs e SLAs (meta sugerida — validar)
│   ├── Prazo de aprovação do cliente · prazo de ajuste interno
│   └── Tempo de resposta a comentários e directs
└── Account apresenta ao cliente → Gate G1

Dia 10: Planejamento do 1º mês
├── Analista → calendário editorial (datas, temas, formatos, funil)
├── Content Creator (apoia) → rascunho de pautas e legendas-modelo
└── Supervisão revisa antes do envio
```

### Semana 3: 1º calendário aprovado (se necessário)

```
Dia 11–13: Aprovação e ajustes
├── Analista → envia calendário ao cliente (handoff Social→Cliente)
├── Cliente aprova por escrito (registro rastreável)
├── Analista consolida feedback em um único documento (handoff Cliente→Social)
└── Calendário aprovado → Gate G2 → início da Fase 3 (../playbooks/fase-3-producao.md)

Dia 14–15: Retrospectiva do onboarding
└── Supervisão + Account → o que travou, o que ajustar no próximo onboarding
```

## Quality gates

### G1 — Plano estratégico aprovado
- [ ] Escopo assinado registrado no VJOB com canais, volume e verba
- [ ] Aprovadores autorizados definidos por escrito (nome do papel, canal, prazo)
- [ ] Canal oficial de aprovação definido e comunicado
- [ ] Todos os acessos testados (login e permissão de publicação/anúncio)
- [ ] Guia de tom de voz validado pelo cliente
- [ ] Auditoria de redes e mídia revisada por humano
- [ ] KPIs e SLAs aceitos pelo cliente (meta sugerida — validar)

### G2 — 1º calendário aprovado
- [ ] Calendário cobre todas as datas relevantes do mês e da praça
- [ ] Cada pauta tem tema, objetivo, etapa do funil, formato e direcionamento
- [ ] Revisado pela Supervisão antes do envio ao cliente
- [ ] Aprovação do cliente registrada por escrito

## Riscos

| Risco | Sinal | Mitigação |
|-------|-------|-----------|
| Acessos atrasados | Semana 1 termina sem Meta Business Suite | Account escala ao cliente no dia 4; checklist enviado já no kickoff |
| Aprovador indefinido | Várias pessoas do cliente opinando | Registrar aprovadores autorizados no G1; demais opiniões passam pelo aprovador |
| Briefing incompleto | Pautas voltam com "não é isso" | Kickoff com roteiro fixo; tom de voz com exemplos certo/errado |
| Carteira sobrecarregada | Analista com mais contas que a capacidade | Supervisão revisa carteira antes de designar; Diretoria de Operações valida realocação |
| Expectativa acima do escopo | Cliente pede canais ou volume não contratados | Account e Supervisão avaliam impacto no escopo antes de aceitar |

## Métricas de sucesso (meta sugerida — validar)

| Métrica | Meta sugerida — validar |
|---------|-------------------------|
| Tempo do contrato assinado ao 1º calendário aprovado | ≤ 15 dias úteis |
| Acessos completos | até o 5º dia útil |
| Rodadas de ajuste no 1º calendário | ≤ 2 |
| Guia de tom de voz validado | até o fim da semana 1 |
| Aprovadores autorizados registrados | 100% antes do 1º envio |

## Roster (slugs para runbooks.json)

```
Núcleo — activation: "sempre"
  sales-account-strategist
  design-brand-guardian
  marketing-social-media-strategist
  paid-media-auditor
  paid-media-tracking-specialist

Especialistas — activation: "semana 1+"
  marketing-content-creator
  marketing-instagram-curator
  marketing-seo-specialist
  marketing-aeo-foundations

Apoio — activation: "sob demanda"
  marketing-tiktok-strategist
  marketing-growth-hacker
```

---

*Método: Ciclo de Operação da Agência (CICLO). Handoffs: [../coordination/handoff-templates.md](../coordination/handoff-templates.md). Prompts: [../coordination/agent-activation-prompts.md](../coordination/agent-activation-prompts.md).*
