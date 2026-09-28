# 📋 Templates de Handoff — Ciclo de Operação da Agência

> Modelos padronizados para cada passagem de trabalho entre áreas. Handoff incompleto é a principal causa de retrabalho, atraso e feedback fragmentado.
>
> **Como usar**: copie o bloco, preencha todos os campos marcados com `*` (obrigatórios) e registre no card do VJOB/iClips. Handoff sem campo obrigatório **volta ao remetente**.

## Regras gerais

- **VJOB é a fonte da verdade** de tarefas e prazos; **iClips** guarda o card da peça e as alterações.
- Todo handoff fica **registrado por escrito** no card. Conversa de WhatsApp ou áudio não substitui o registro.
- Datas no formato DD/MM/AAAA; valores em R$.
- Agentes de IA podem **rascunhar** o handoff. Um humano confere e envia.
- Nenhum template contém dado pessoal de consumidor. Use apenas o necessário e anonimize prints.

| # | Template | De → Para | Fase |
|---|---|---|---|
| 1 | [Entrada de demanda](#account--social) | Account → Social | Transversal / [Fase 2](../playbooks/fase-2-planejamento-mensal.md) |
| 2 | [Briefing padronizado de peça](#social--da) | Social → D.A. | [Fase 3](../playbooks/fase-3-producao.md) |
| 3 | [Envio para aprovação](#social--cliente) | Social → Cliente | [Fase 4](../playbooks/fase-4-aprovacao.md) |
| 4 | [Consolidação de feedback (rodada)](#cliente--social) | Cliente → Social | [Fase 4](../playbooks/fase-4-aprovacao.md) |
| 5 | [Peça aprovada para mídia](#social--tráfego) | Social → Tráfego | [Fase 5](../playbooks/fase-5-publicacao-e-midia.md) |
| 6 | [Interações que exigem o Cliente](#social--sac) | Social → SAC / Cliente | [Fase 5](../playbooks/fase-5-publicacao-e-midia.md) |
| 6b | [Ficha da marca para SAC](#ficha-da-marca-para-sac) | Analista da conta → SAC | [Fase 5](../playbooks/fase-5-publicacao-e-midia.md) |
| 6c | [Ata de alinhamento com o cliente](#ata-de-alinhamento-com-o-cliente) | Reunião → Social | [Fase 3](../playbooks/fase-3-producao.md) |
| 7 | [Relatório de operação mensal](#supervisão--diretoria-de-operações) | Supervisão → Diretoria de Operações | [Fase 6](../playbooks/fase-6-resultados.md) |
| 8 | [Escalonamento de atraso/risco](#escalonamento-de-atraso) | Qualquer papel → nível acima | Transversal |
| 9 | [Fechamento de fase (gate)](#fechamento-de-fase) | Dono da fase → próxima fase | Todas |

## Account → Social

**Entrada de demanda.** Use sempre que uma demanda chegar do Cliente pelo Account. A triagem **planejado × extra** é feita pela Supervisão junto com o Account.

```markdown
# Entrada de demanda

| Campo | Valor |
|---|---|
| **Cliente*** | [Segmento / identificação interna da conta] |
| **Solicitante*** | [Papel: Account] |
| **Data de entrada*** | [DD/MM/AAAA HH:MM] |
| **Canal de origem*** | [WhatsApp / e-mail / reunião / VJOB] |
| **Card VJOB*** | [nº do card] |

**O que o Cliente pediu***: [Descrição objetiva, em uma ou duas frases]
**Objetivo***: [Vender oferta / divulgar ação de loja / institucional / engajamento / outro]
**Formato e quantidade***: [Feed / carrossel / Reels / Stories / anúncio — quantidade]
**Prazo desejado pelo Cliente***: [DD/MM/AAAA]

## Materiais recebidos
- [ ] Ofertas (preço, validade, condições)  - [ ] Fotos / vídeos / logos  - [ ] Referências
- [ ] Nada recebido — pendente: [o quê, até quando]

## Triagem (preenche a Supervisão)*
- [ ] **Planejado** — já consta no calendário do mês
- [ ] **Extra dentro do escopo** — cabe na capacidade sem impacto
- [ ] **Extra com impacto no escopo** — exige alinhamento Account + Cliente
- [ ] **Outra área** — repassar para: [Criação / Tráfego / SAC / Fast Mídia / outra]

**Prioridade***: [Alta / Média / Baixa]
**Analista responsável***: [Papel / equipe: Sede / House / SAC]
**Prazo interno acordado***: [DD/MM/AAAA]
**Observações**: [...]
```

## Social → D.A.

**Briefing padronizado de peça.** Briefing incompleto gera retrabalho. D.A. pode devolver o card se faltar campo obrigatório.

```markdown
# Briefing de peça

| Campo | Valor |
|---|---|
| **Cliente*** | [Segmento / identificação interna] |
| **Card iClips / VJOB*** | [nº] |
| **Analista responsável*** | [Papel] |
| **Data de entrega da arte*** | [DD/MM/AAAA HH:MM] |
| **Data de publicação*** | [DD/MM/AAAA HH:MM] |

## Pauta*
- **Tema**: [...]
- **Objetivo**: [...]
- **Etapa do funil**: [Descoberta / Consideração / Conversão / Relacionamento]
- **Formato e dimensão**: [Feed 1080×1350 / Stories 1080×1920 / Reels / carrossel N telas]
- **Rede(s)**: [Instagram / Facebook / TikTok / outra]

## Texto na arte (copy)*
[Título, subtítulo, oferta, preço, validade, observações legais — texto final]

**CTA***: [Ex.: "Peça pelo WhatsApp", "Link na bio", "Visite a loja"]

## Direcionamento de arte*
[Estilo, elementos obrigatórios, hierarquia visual]

## Referências*
[Links ou anexos; o que aproveitar de cada uma]

## Materiais anexos
- [ ] Logo / guia de marca  - [ ] Fotos de produto  - [ ] Fontes / paleta  - [ ] Vídeo bruto

## Restrições
- [ ] Peça vai para mídia paga (checar política de anúncio e POP VAN-POP-MKT-001)
- [ ] Contém imagem de pessoas (autorização de uso confirmada)
- [ ] Contém alegação de saúde, preço ou comparação (checar CONAR)

**Legenda (para contexto, não vai na arte)**: [...]
```

## Social → Cliente

**Envio para aprovação.** Envie em lote organizado. O prazo de retorno é **explícito** em toda mensagem.

```markdown
# Envio para aprovação

| Campo | Valor |
|---|---|
| **Cliente*** | [Identificação interna] |
| **Aprovador autorizado*** | [Papel definido no onboarding] |
| **Data e hora do envio*** | [DD/MM/AAAA HH:MM] |
| **Prazo de retorno*** | [DD/MM/AAAA HH:MM] (janela: meta sugerida — validar) |
| **Canal*** | [E-mail / WhatsApp / registro rastreável conforme POP] |

## Peças deste lote*
| # | Card | Formato | Data de publicação | Rodada |
|---|---|---|---|---|
| 1 | [nº] | [Feed] | [DD/MM/AAAA HH:MM] | [1ª] |
| 2 | [nº] | [Stories] | [DD/MM/AAAA HH:MM] | [1ª] |

## Mensagem ao Cliente (modelo)
"Olá! Seguem [N] peças para aprovação, com publicação prevista entre [DD/MM] e [DD/MM].
Por favor, responda **por escrito** até [DD/MM/AAAA HH:MM] com 'Aprovado' ou com os ajustes
numerados por peça. Sem retorno até o prazo, as peças não serão publicadas e a data será reagendada."

## Lembretes programados*
- [ ] 1º lembrete: [DD/MM/AAAA HH:MM]
- [ ] 2º lembrete (vencimento): [DD/MM/AAAA HH:MM]
- [ ] Sem retorno → escalonar (template 8)

## Mídia paga
- [ ] Peça segue fluxo do POP VAN-POP-MKT-001 (rascunho, em aprovação)
```

## Cliente → Social

**Consolidação de feedback (rodada). Um único registro por card/peça.** Tudo que chegar por WhatsApp, áudio, e-mail ou ligação é transcrito aqui pelo Analista.

```markdown
# Consolidação de feedback

| Campo | Valor |
|---|---|
| **Card iClips / VJOB*** | [nº] |
| **Rodada*** | [1ª / 2ª / 3ª — acima do limite exige Supervisão] |
| **Quem enviou o feedback*** | [Papel do aprovador autorizado] |
| **Data e hora*** | [DD/MM/AAAA HH:MM] |
| **Canais de origem*** | [WhatsApp / áudio / e-mail / ligação] |

## Ajustes solicitados (numerados)*
| # | Onde (arte / legenda / vídeo) | Ajuste pedido | Responsável | Status |
|---|---|---|---|---|
| 1 | [Arte] | [...] | [D.A.] | [Pendente / Feito] |
| 2 | [Legenda] | [...] | [Analista] | [Pendente / Feito] |

## Classificação*
- [ ] Ajuste dentro do briefing aprovado
- [ ] Mudança de briefing → avaliar como extra (Supervisão + Account)
- [ ] Ajuste conflita com política de anúncio / CONAR / LGPD → explicar ao Cliente

## Confirmação*
- [ ] Ajustes lidos de volta ao Cliente e confirmados por escrito
- [ ] Nova data de reenvio: [DD/MM/AAAA HH:MM]

## Aprovação final (quando houver)*
- [ ] "Aprovado" por escrito anexado (print / e-mail) em [DD/MM/AAAA HH:MM]
```

## Social → Tráfego

**Peça aprovada para mídia paga**, com UTM e rastreamento. Só entra peça com aprovação registrada.

```markdown
# Peça aprovada para mídia paga

| Campo | Valor |
|---|---|
| **Cliente*** | [Identificação interna] |
| **Card*** | [nº] |
| **Aprovação registrada*** | [Link / print — DD/MM/AAAA] |
| **POP VAN-POP-MKT-001 cumprido*** | [Sim / Não — motivo] |

## Campanha*
- **Objetivo**: [Alcance / tráfego / mensagens / conversão / vendas]
- **Plataforma**: [Meta / Google / TikTok]
- **Tipo**: [Impulsionamento de post / campanha nova / inclusão em campanha ativa]
- **Verba aprovada**: R$ [valor] — [diária / total]
- **Período**: [DD/MM/AAAA] a [DD/MM/AAAA]
- **Público / praça**: [...]

## Destino*
- **URL / WhatsApp / perfil**: [...]
- **UTM***: `utm_source=[meta|google]&utm_medium=[cpc|paid_social]&utm_campaign=[cliente_acao_mmaaaa]&utm_content=[peca_nº]`

## Rastreamento*
- [ ] Pixel / CAPI / GA4 verificados (Tracking & Measurement Specialist pode apoiar)
- [ ] Evento de conversão definido: [...]

## Arquivos*
- [ ] Criativo final (dimensões por posicionamento)  - [ ] Texto principal, título e descrição aprovados

**Retorno esperado do Tráfego**: confirmação de ativação e aviso de reprovação ou comentário em anúncio.
```

## Social → SAC

**Interações que exigem resposta do Cliente** (preço, estoque, reclamação, troca, jurídico). Nada é respondido por suposição.

```markdown
# Repasse de interações

| Campo | Valor |
|---|---|
| **Cliente*** | [Identificação interna] |
| **Data e hora do repasse*** | [DD/MM/AAAA HH:MM] |
| **Destinatário*** | [SAC / papel indicado pelo Cliente] |
| **Prazo para retorno*** | [DD/MM/AAAA HH:MM] (meta sugerida — validar) |

## Interações*
| # | Rede / local | Tipo | Tema | Resumo (sem dados pessoais) | Urgência |
|---|---|---|---|---|---|
| 1 | [Instagram / direct] | [Reclamação] | [Troca] | [...] | [Alta] |
| 2 | [Facebook / comentário] | [Dúvida] | [Estoque] | [...] | [Média] |

## Classificação*
- [ ] Preço / estoque / disponibilidade  - [ ] Reclamação / troca / devolução  - [ ] Saúde / produto regulado
- [ ] Jurídico / imprensa / risco de crise → escalonar (template 8)

## Retorno
- **Resposta do Cliente**: [...]
- **Respondido ao público em**: [DD/MM/AAAA HH:MM] por [Analista / SAC]
- **Status***: [Aberto / Respondido / Encerrado]
```

## Ficha da marca para SAC

**Base de consulta do atendimento.** Mantida pelo Analista da conta com informações do Cliente; atualizada antes de cada campanha. Todos que atendem a conta usam a mesma ficha.

```markdown
# Ficha da marca — [identificação interna]

| Campo | Valor |
|---|---|
| **Tom de voz e tratamento*** | [ex.: próximo, "você", emojis moderados] |
| **Canais oficiais de contato*** | [WhatsApp, telefone, site — só os oficiais] |
| **Horários e endereços*** | [lojas/unidades] |
| **Atualizada em*** | [DD/MM/AAAA] por [papel] |

## Campanhas vigentes*
| Campanha | Período | Regras/mecânica | Link do regulamento |
|---|---|---|---|

## Perguntas frequentes com resposta aprovada*
| Pergunta | Resposta aprovada | Aprovada por (papel) |
|---|---|---|

## Encaminhamentos*
| Tema | Para onde direcionar | Prazo de retorno do Cliente |
|---|---|---|
| Preço / estoque | [canal] | [...] |
| Pós-venda / troca | [canal] | [...] |

## Temas proibidos ou sensíveis*
- [ex.: não comentar concorrentes; saúde → sempre privado; jurídico → Supervisão]
```

## Ata de alinhamento com o cliente

**Base de todo briefing que nasce de reunião.** A transcrição sozinha não serve de briefing.

```markdown
# Ata de alinhamento — [identificação interna] — [DD/MM/AAAA]

| Campo | Valor |
|---|---|
| **Participantes (papéis)*** | [Account, Analista, cliente — papéis, sem dados pessoais] |
| **Objetivo da reunião*** | [...] |

## Decisões*
1. [...]

## Informações confirmadas*
| Item | Valor | Confirmado por (papel) |
|---|---|---|
| Oferta / condição | [...] | [...] |
| Datas | [...] | [...] |

## Pendências*
| Pendência | Dono | Prazo |
|---|---|---|

## Próximos passos*
- [Briefings a abrir, com card VJOB]
```

## Supervisão → Diretoria de Operações

**Relatório de operação mensal.** Não confundir com o relatório de conta ao Cliente ([Fase 6](../playbooks/fase-6-resultados.md)).

```markdown
# Relatório de operação — [MÊS/AAAA]

| Campo | Valor |
|---|---|
| **Remetente*** | Supervisão de Social Media |
| **Destinatário*** | Diretoria de Operações |
| **Data de envio*** | [DD/MM/AAAA] |
| **Fonte dos dados*** | VJOB / iClips / Dash |

## Prazo*
- % de tarefas no prazo: [__%] (meta sugerida — validar)
- Atrasos: [quantidade] — principais causas: [aprovação / briefing / volume / outra]

## Volume*
| Equipe | Analistas | Tarefas | Peças | Extras |
|---|---|---|---|---|
| Sede | [n] | [n] | [n] | [n] |
| House | [n] | [n] | [n] | [n] |
| SAC | [n] | [n] | — | [n] |

## Qualidade*
- Aprovação na 1ª rodada: [__%]
- Rodadas médias por peça: [__]
- Ocorrências de publicação: [n] — [resumo]

**Auditoria de redes**: [Achados e correções do período]

## Capacidade e carteira*
- Analistas acima da capacidade: [n] — [equipe]
- Riscos: [...]

## Decisões solicitadas à Diretoria*
1. [...]
2. [...]
```

## Escalonamento de atraso

**Escalonamento de atraso ou risco.** Cadeia: **Analista → Supervisão → Account → Diretoria de Operações**. Suba um nível quando o anterior não resolver no prazo.

```markdown
# Escalonamento

| Campo | Valor |
|---|---|
| **Cliente*** | [Identificação interna] |
| **Card(s)*** | [nº] |
| **Aberto por*** | [Papel] |
| **Escalado para*** | [Supervisão / Account / Diretoria de Operações] |
| **Data e hora*** | [DD/MM/AAAA HH:MM] |
| **Nível*** | [1 Supervisão / 2 Account / 3 Diretoria] |

## Tipo*
- [ ] Atraso de aprovação do Cliente  - [ ] Rodadas acima do limite  - [ ] Briefing / material incompleto
- [ ] Sobrecarga de capacidade  - [ ] Risco de reputação / crise
- [ ] Problema de mídia paga (reprovação, verba, rastreamento)

**Situação***: [O que aconteceu, desde quando, o que já foi tentado]
**Impacto***: [Peças / datas afetadas; risco para o Cliente; impacto no escopo]
**Decisão necessária***: [O que se pede ao nível acima, com prazo: DD/MM/AAAA HH:MM]

## Desfecho
- **Decisão tomada**: [...] por [Papel] em [DD/MM/AAAA]
- **Status***: [Aberto / Resolvido]
```

## Fechamento de fase

**Fechamento de fase (gate).** Preenchido pelo dono humano da fase; a próxima fase só começa com o recebimento registrado.

```markdown
# Fechamento de fase

| Campo | Valor |
|---|---|
| **Cliente / campanha*** | [Identificação interna] |
| **Modo*** | [Conta completa / Campanha / Demanda pontual] |
| **Fase*** | [0–6 — nome] |
| **Gate*** | [G0–G6] |
| **Dono humano da fase*** | [Papel] |
| **Data*** | [DD/MM/AAAA] |

## Checklist do gate*
[Colar o Quality Gate do playbook da fase com cada item marcado]

## Veredito*
- [ ] **Aprovado** — segue para a Fase [N+1]
- [ ] **Aprovado com ressalvas** — ressalvas: [...] prazo: [DD/MM/AAAA]
- [ ] **Não aprovado** — volta para: [etapa]

## Entregáveis repassados*
- [...] (link no VJOB / iClips)

**Agentes de IA utilizados**: [Agente — para quê — revisado por (Papel)]
**Pendências e riscos**: [...]

**Recebido por (próxima fase)***: [Papel] em [DD/MM/AAAA]
```

---

Voltar ao documento-mestre: [Ciclo de Operação da Agência](../ciclo-agencia.md)

<sub>Adaptado do NEXUS (templates de handoff entre agentes de software) para a operação de agência.</sub>
