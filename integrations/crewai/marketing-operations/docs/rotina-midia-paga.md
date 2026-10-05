# Rotina de Mídia Paga e Performance parametrizada na crew

Fonte: formulários de levantamento da rotina profissional de **Carlos André** (Analista de Mídia Paga, 1 ano na função) e **João Araújo** (Supervisor de Mídia
Paga, 1 ano e 6 meses), preenchidos em 18/09/2026, setor Mídia Paga / Performance, diretoria de operações Jéssica Nery.
Parâmetros no arquivo `src/marketing_ops/config/rotina_midia.yaml`, que alimenta os prompts e as travas em código.

## 1. Onde cada parte da rotina entrou

| Rotina (formulário) | Agente | Tarefa | Como foi parametrizado |
|---|---|---|---|
| Subida de nova campanha (briefing → público/verba/objetivo → UTM → subir → revisão do Supervisor → ativar) | Gestor de Mídia Paga | `plano_midia_paga` | Fluxo no prompt; a ativação só ocorre depois do G3 (a crew não escreve em plataforma) |
| Checagem diária de orçamento e saldo (budget pace) | Gestor de Mídia Paga | `plano_midia_paga` | Seção "Rotina operacional": budget pace diário e alerta aos **90%** do orçamento; trava exige os dois |
| Otimização diária (CPA, CPL, ROAS, CTR; pausar, remanejar verba, pedir criativos) | Gestor de Mídia Paga | `plano_midia_paga` | Rotina diária e semanal descritas no plano |
| Alteração de verba sem registro formal (dificuldade 3) | Gestor / Supervisor | `plano_midia_paga`, `auditoria_midia` | Regra: só vale por e-mail ou chamado no VJOB |
| Briefing incompleto (dificuldade 2) | Gestor de Mídia Paga | `plano_midia_paga` | Seção "Insumos e pendências": verba, objetivo, público; o que faltar vira [VALIDAR] |
| Criativos entregues em cima do prazo (dificuldade 1) | Gestor / Supervisor | `plano_midia_paga`, `auditoria_midia` | Item CRIATIVOS da auditoria e prazo crítico no prompt |
| Variações de copy com IA (item 9) | Gestor de Mídia Paga | `plano_midia_paga` | Variações A/B a partir do briefing, sempre revisadas (marca, plataforma, [VALIDAR]) |
| Autonomia x autorização (item 4) | Gestor, Supervisor | `plano_midia_paga`, `auditoria_midia` | Duas listas no prompt; seção "Alçadas e autorizações" obrigatória; item ALÇADAS na auditoria |
| Supervisão de qualidade técnica e auditoria de campanhas (segmentação, pixel/CAPI, criativos, URLs, copies) | Supervisor de Mídia Paga (**novo**, 14º agente) | `auditoria_midia` | Sete itens OK/PENDENTE/FALHA e parecer LIBERAR PARA G2 ou DEVOLVER AO GESTOR; cruza com a varredura em código |
| Auditoria de pixel e rastreamento (GTM → eventos de teste → GA4/Gerenciador → atribuição) | Analista de Dados | `plano_medicao` | Checklist no prompt e na ficha |
| Relatório mensal (coletar → template → análise → validação do Supervisor → Account) | Analista de Dados | `relatorio_performance` | Fluxo e status "aguardando validação do Supervisor"; KPIs da rotina |
| Indicadores (ROAS, CPA, CPL, CTR, CPM, conversão do funil, budget pace, retrabalho) | Gestor, Analista | `plano_midia_paga`, `plano_medicao` | Lista única no YAML |

## 2. Alçadas (RACI resumido)

| Decisão | Gestor de Mídia | Supervisor | Diretoria de Operações |
|---|---|---|---|
| Pausar criativos, ajustar verba diária dentro do limite, testar públicos e formatos | **R** (autonomia) | I | — |
| Revisão técnica antes de ativar | R | **A** (audita) | — |
| Alterar orçamento total ou verba fora do contrato | C | R | **A** |
| Criar estrutura que mude o escopo contratado | C | R | **A** |
| Enviar relatório mensal ao cliente | R | **A** (valida) | I |
| Repactuar prazo com impacto na entrega | R | **A** | I |

## 3. Travas em código
- `plano_midia_paga`: o plano precisa citar budget pace, alerta de 90%, UTM, revisão técnica do Supervisor e autorização; mais as travas de mídia já existentes
  (canal fora do brief, projeção sem [VALIDAR], conversões que não fecham).
- `auditoria_midia`: sete linhas, parecer coerente (FALHA ⇒ DEVOLVER) e varredura cruzada com o plano de mídia.
- Pedido do G2: copia literalmente as linhas da auditoria.

## 4. O que a rotina pede e a crew ainda não faz
Itens do formulário (seção 9) que exigem escrita em plataformas ou integrações e ficam fora do escopo atual (a publicação real está desligada):
- alertas automáticos de saldo baixo e de 90% do orçamento (script de notificação por e-mail ou Slack);
- auditoria em massa de UTMs e tags por script;
- consolidação automática dos relatórios no Looker Studio;
- agente que leia a tabela de desempenho de criativos e recomende pausas.
Também não estão cobertos por serem de gestão de pessoas e não de campanha: reuniões 1:1 no Qulture, reestruturação de carteiras, plano de contingência por ausência e
controle de atrasos no VJOB. Hoje a crew trata a regra de VJOB só como prazo crítico.

## 5. Limites
- O formulário descreve a rotina **operacional** (execução em plataformas); a crew produz o plano e a auditoria, e a execução depende do G3 e de uma pessoa.
- As metas numéricas dos formulários (ROAS, CPA, CPL) são combinadas por cliente e não foram tomadas como padrão: ficam [VALIDAR] no plano.
- Validação dos formulários pelos responsáveis (liderança, diretoria) estava em branco em 18/09/2026.
