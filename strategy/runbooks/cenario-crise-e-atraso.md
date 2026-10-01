# 🚨 Runbook: Crise de Reputação ou Atraso Crítico

> **Modo**: Demanda pontual (NEXUS-Micro) | **Duração**: minutos a dias | **Agentes**: 3–8

---

## Cenário

Este runbook tem **dois gatilhos**:

- **(a) Crise de reputação em rede social** — comentários negativos em volume, post publicado com erro de preço ou oferta, reclamação que viraliza, marca citada em polêmica.
- **(b) Atraso crítico** — entrega interna ou aprovação do cliente que ameaça a data de publicação (oferta com validade, data comemorativa, ação de loja).

Rapidez importa, mas **nenhuma resposta pública sai sem aprovação humana**. Agentes de IA ajudam a diagnosticar, redigir rascunhos e organizar a linha do tempo. Quem decide é a cadeia de escalonamento.

Fases relacionadas: [Fase 4 — Aprovação](../playbooks/fase-4-aprovacao.md) · [Fase 5 — Publicação](../playbooks/fase-5-publicacao-e-midia.md) · [Fase 6 — Resultados](../playbooks/fase-6-resultados.md). Template de escalonamento: [../coordination/handoff-templates.md](../coordination/handoff-templates.md).

## Severidades

| Nível | Definição | Exemplos | Resposta inicial (meta sugerida — validar) |
|-------|-----------|----------|--------------------------------------------|
| **S1 — Crítica** | Risco à reputação ou financeiro imediato | Preço errado com pedidos entrando; reclamação viral; oferta de campanha paga sem aprovação | ≤ 30 min, escala até a Diretoria de Operações |
| **S2 — Alta** | Impacto visível, contido | Onda de comentários negativos num post; peça de data fixa sem aprovação a 24 h da publicação | ≤ 2 h, escala até o Account |
| **S3 — Média** | Impacto baixo, com contorno | Erro de digitação publicado; atraso de peça sem data fixa | ≤ 1 dia útil, Supervisão resolve |
| **S4 — Baixa** | Sem impacto externo | Tarefa atrasada no VJOB sem risco de data | Próxima daily |

## Cadeia de escalonamento

```
Analista de Social Media → Supervisão de Social Media → Account → Diretoria de Operações
        (detecta)              (classifica e coordena)    (fala com o cliente)   (casos S1 e decisões de capacidade)
```

Regra: quem detecta avisa a Supervisão **imediatamente** (Google Chat ou WhatsApp interno) e registra no VJOB. Ninguém responde publicamente nem apaga post sem decisão da Supervisão + Account.

## Roster de agentes

### Núcleo
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| PR & Communications Manager | Rascunho de nota, resposta-padrão e mensagem ao cliente | Account |
| Social Media Strategist | Leitura do volume e do teor dos comentários; plano de moderação | Supervisão de Social Media |
| Brand Guardian | Checagem de tom da resposta frente à identidade do cliente | Supervisão de Social Media |

### Especialistas
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Twitter Engager | Modelos de resposta individual a comentários e directs | Analista de Social Media / SAC |
| X/Twitter Intelligence Analyst | Monitoramento de menções e propagação fora do perfil | Supervisão de Social Media |
| Paid Social Strategist | Pausa ou ajuste de anúncios afetados | Tráfego (Mídia Paga) |
| Ad Creative Strategist | Peça corrigida e checagem de políticas | Tráfego (Mídia Paga) |

### Apoio
| Agente | Papel no cenário | Humano responsável |
|--------|------------------|--------------------|
| Content Creator | Reescrita rápida de legenda ou peça no gatilho (b) | Analista de Social Media |
| Account Strategist | Plano de recuperação da relação com o cliente | Account |

## Plano de execução

### Gatilho (a): crise de reputação

```
Minuto 0–15: Detecção e contenção
├── Analista / SAC → detecta e avisa a Supervisão; print de tudo
├── Supervisão → classifica severidade (S1–S4)
├── Se erro de preço/oferta: Supervisão decide arquivar/editar o post
│   └── Tráfego pausa anúncios ligados ao post (Paid Social Strategist apoia)
└── Registro no VJOB: horário, link, prints, severidade

Minuto 15–60: Diagnóstico e resposta
├── Social Media Strategist (apoia) → volume, temas das reclamações, perfis influentes
├── X/Twitter Intelligence Analyst (apoia) → propagação fora do perfil
├── PR & Communications Manager (apoia) → rascunho de nota e resposta-padrão
├── Brand Guardian (apoia) → ajuste de tom
├── Account → alinha com o cliente e obtém aprovação escrita da resposta
└── Analista / SAC → publica a resposta aprovada e responde individualmente
    (Twitter Engager apoia com modelos; nada de dados pessoais em público)

Horas seguintes: monitoramento
├── Supervisão → checa volume a cada 2 h (S1) ou 4 h (S2)
└── Account → atualiza o cliente até estabilizar
```

### Gatilho (b): atraso crítico

```
Detecção (check diário de atrasos no VJOB ou alerta do Analista)
├── Supervisão → identifica gargalo: briefing, criação, ajuste ou aprovação do cliente
└── Classifica severidade pela distância até a data de publicação

Ação conforme o gargalo
├── Interno (criação/ajuste)
│   ├── Supervisão → repriorização na daily; realoca com a Head de Criação
│   └── Content Creator (apoia) → acelera texto/roteiro
├── Aprovação do cliente
│   ├── Analista → lembrete formal pelo canal oficial
│   ├── Account → contato direto com o aprovador autorizado
│   └── Handoff "Escalonamento de atraso" com data-limite e consequência
└── Sem solução até a data-limite
    ├── Account propõe ao cliente: adiar, publicar versão reduzida ou cancelar
    └── Diretoria de Operações decide em S1 (impacto contratual ou de carteira)
```

### Pós-mortem (até 3 dias úteis após o encerramento)

```
├── Supervisão conduz (30–45 min), sem busca de culpados
├── Linha do tempo: detecção → decisão → resposta → estabilização
├── Causa raiz e ponto do Ciclo onde falhou (G3? G4? G5?)
├── Ações preventivas com dono e prazo (ex.: item novo no checklist)
└── Supervisão → registra no relatório de operação à Diretoria de Operações
```

## Comunicação com o cliente

- O Account é o único canal oficial com o cliente durante o incidente.
- Primeira mensagem: o que aconteceu, o que já foi feito, próxima atualização em quanto tempo.
- Respostas públicas e notas só saem com aprovação escrita do cliente.
- Encerramento: resumo do incidente e ações preventivas.

## Quality gates

- [ ] Severidade classificada e registrada no VJOB
- [ ] Prints e links preservados antes de qualquer edição ou arquivamento
- [ ] Anúncios afetados pausados (quando aplicável)
- [ ] Resposta pública aprovada por escrito pelo cliente
- [ ] Nenhum dado pessoal de consumidor exposto nas respostas
- [ ] Cliente atualizado no intervalo combinado
- [ ] Pós-mortem feito, com ações preventivas com dono e prazo

## Riscos

| Risco | Mitigação |
|-------|-----------|
| Resposta impulsiva agrava a crise | Nada público sem Supervisão + Account + aprovação do cliente |
| Apagar post gera efeito contrário | Decidir entre editar, arquivar ou manter com nota; preservar evidências |
| Texto de IA fora de contexto | Rascunho sempre revisado pelo Brand Guardian (apoio) e pela Supervisão |
| Atraso recorrente do mesmo aprovador | Registrar no pós-mortem; Account renegocia SLA |
| Crise sem dono fora do horário | Escala de plantão definida pela Supervisão (meta sugerida — validar) |

## Métricas de sucesso (meta sugerida — validar)

| Métrica | Meta sugerida — validar |
|---------|-------------------------|
| Tempo até a 1ª ação de contenção (S1) | ≤ 30 min |
| Tempo até a resposta pública aprovada (S1/S2) | ≤ 2 h |
| Publicações perdidas por atraso crítico | zero por mês |
| Pós-mortems concluídos no prazo | 100% dos S1 e S2 |
| Reincidência da mesma causa raiz | zero em 90 dias |

## Roster (slugs para runbooks.json)

```
Núcleo — activation: "sempre"
  marketing-pr-communications-manager
  marketing-social-media-strategist
  design-brand-guardian

Especialistas — activation: "S1 e S2"
  marketing-twitter-engager
  marketing-x-twitter-intelligence-analyst
  paid-media-paid-social-strategist
  paid-media-creative-strategist

Apoio — activation: "sob demanda"
  marketing-content-creator
  sales-account-strategist
```

---

*Método: Ciclo de Operação da Agência (CICLO). Prompts: [../coordination/agent-activation-prompts.md](../coordination/agent-activation-prompts.md).*
