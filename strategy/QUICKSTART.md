# ⚡ Guia Rápido — Ciclo de Operação da Agência

> Comece em 5 minutos. Método completo em [ciclo-agencia.md](ciclo-agencia.md).

---

## 1. Qual é a sua situação?

| Situação | Modo | Abra este runbook |
|---|---|---|
| Fechamos um cliente novo | Conta completa | [Onboarding de novo cliente](runbooks/cenario-onboarding-cliente.md) |
| É mais um mês de operação da conta | Conta completa (recorrente) | [Ciclo mensal de Social Media](runbooks/cenario-rotina-mensal-social.md) |
| Vem aí uma data comemorativa, ação de loja ou lançamento | Campanha | [Campanha sazonal](runbooks/cenario-campanha-sazonal.md) |
| Precisamos diagnosticar ou assumir contas de Google/Meta Ads | Campanha | [Diagnóstico de mídia paga](runbooks/cenario-auditoria-midia-paga.md) |
| Post com erro, comentário negativo viral ou entrega em risco | Demanda pontual | [Crise ou atraso crítico](runbooks/cenario-crise-e-atraso.md) |

## 2. Em que fase você está?

| Você vai… | Fase | Playbook |
|---|---|---|
| Prospectar, diagnosticar e fazer proposta | 0 | [Prospecção](playbooks/fase-0-prospeccao.md) |
| Receber o cliente e montar o plano | 1 | [Onboarding](playbooks/fase-1-onboarding.md) |
| Montar o calendário e as pautas do mês | 2 | [Planejamento mensal](playbooks/fase-2-planejamento-mensal.md) |
| Briefar o D.A., escrever legenda, roteirizar, editar | 3 | [Produção](playbooks/fase-3-producao.md) |
| Enviar ao cliente e consolidar ajustes | 4 | [Aprovação](playbooks/fase-4-aprovacao.md) |
| Agendar, publicar, responder e impulsionar | 5 | [Publicação e mídia](playbooks/fase-5-publicacao-e-midia.md) |
| Fechar relatório e reunião de resultados | 6 | [Resultados](playbooks/fase-6-resultados.md) |

## 3. Ative um agente em 3 passos

1. Instale os agentes ativos na sua ferramenta:
   ```bash
   ./scripts/install.sh --tool claude-code
   ```
2. Copie o prompt da fase em [agent-activation-prompts.md](coordination/agent-activation-prompts.md) e troque os campos entre colchetes (`[CLIENTE]`, `[TOM DE VOZ]`, `[OBJETIVO]`…).
3. **Revise a saída** antes de mandar ao cliente ou publicar. A IA faz a primeira versão; a responsabilidade é de quem assina a fase.

Exemplo, briefing para o D.A.:
```
Ative o Content Creator. Transforme este pedido em briefing padronizado para o D.A.
Cliente: [CLIENTE] · Segmento: [SEGMENTO] · Tom de voz: [TOM DE VOZ]
Pedido: [TEXTO DO PEDIDO]
Devolva: objetivo, formato e medidas, texto da arte, legenda, CTA, referências, prazo e dúvidas em aberto.
```

### Pelo app Agency Agents (desktop)

O app lê qualquer clone deste repositório como catálogo. Ele mostra as 4 divisões, os 39 agentes e os 5 runbooks da agência, e ignora o `_arquivo/`.

1. Clone o repositório da agência numa pasta local:
   ```bash
   git clone https://github.com/jussaracavalcante-sketch/agency-agents.git
   ```
2. Abra o app → **Configurações → Catálogo → Alternar fonte → Use seu próprio clone → Escolha a pasta…** e selecione a pasta clonada.
3. Marque **"Deixe o aplicativo manter meu clone atualizado"**. A fonte passa a aparecer como **Seu clone (gerenciado)**, e o app atualiza o catálogo com `git pull --ff-only`. Desmarcado, o clone fica somente leitura.
4. Instale os agentes na ferramenta desejada (Claude Code, Cursor, Codex, Gemini CLI…) pelo próprio app.

> A opção **Clone gerenciado** do app clona o catálogo público original, não o da agência. Use sempre o clone próprio.



1. **Demanda que não está no VJOB não existe.** WhatsApp é conversa; VJOB é registro.
2. **O Social trabalha a partir do planejado.** Extra passa pelo filtro Account + Supervisão.
3. **Briefing sem os campos obrigatórios volta.** Use o [modelo](coordination/handoff-templates.md).
4. **Nada vai ao ar sem aprovação escrita** do aprovador autorizado, registrada no card.
5. **IA apoia, pessoa decide.** Sem dado pessoal em prompt; imagem de pessoa real só com autorização.

## 5. Onde pedir ajuda

| Assunto | Fale com |
|---|---|
| Prioridade, prazo, carga de trabalho | Supervisão de Social Media |
| Escopo, expectativa do cliente, extra | Account |
| Qualidade visual | Head de Criação |
| Verba, campanha paga, rastreamento | Supervisão de Mídia Paga |
| Capacidade da equipe, caso grave | Diretoria de Operações |
