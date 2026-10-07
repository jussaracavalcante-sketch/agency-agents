# Dossiê de prontidão do piloto: compliance, segurança e LGPD

**Escopo:** Equipe de Operação de Marketing (14 agentes, portões G1/G2/G3), portal de aprovação, Supabase e funções de webhook.
**Data-base:** 07/10/2026. **Status:** levantamento técnico concluído; itens jurídicos e contratuais pendem de validação do jurídico e do encarregado.
**Limite deste documento:** é uma avaliação técnica. Não substitui parecer jurídico nem o RIPD assinado pelo controlador.

## 1. Resumo executivo

O piloto pode seguir para os analistas em formato **interno, restrito e assistido**, desde que as condições da seção 9 sejam cumpridas. A arquitetura já tem os controles mais importantes: decisão humana em três portões, publicação desligada, perfis por convite, auditoria de ações e chave de serviço só no servidor. Os riscos relevantes estão em três frentes.

| Frente | Situação | Risco se lançar hoje |
|---|---|---|
| Segurança técnica | Boa base; faltam cabeçalhos HTTP, privilégios mínimos no banco, segundo administrador e autenticação em dois fatores | Médio |
| LGPD | Nenhum dado pessoal de pacientes encontrado nos 738 eventos gravados; faltam registro de tratamento, RIPD, encarregado, contratos com suboperadores e política de retenção | Alto, por ausência de documentação |
| Conteúdo regulado (saúde) | Há superlativos que passam pelo Guardião; a decisão humana é a barreira | Médio, contido pelos portões e pela publicação desligada |

## 2. Dados tratados e finalidades

| Categoria | Titular | Onde fica | Finalidade | Base legal sugerida (validar) | Retenção proposta |
|---|---|---|---|---|---|
| Nome, e-mail corporativo, cargo, papel | Analistas e aprovadores | Supabase (São Paulo), tabelas de perfis, convites e auditoria | Acesso, responsabilização das decisões | Execução de contrato de trabalho e legítimo interesse (art. 7º, V e IX) | Vigência do vínculo mais prazo legal |
| Sessão, data e hora das ações | Usuários do portal | Auditoria | Trilha de auditoria e segurança | Legítimo interesse e prevenção a fraudes | 5 anos, somente de acréscimo |
| Briefing da campanha | Clientes, pessoa jurídica | Portal, plataforma de agentes, eventos do webhook | Produzir a campanha contratada | Execução de contrato com o cliente | 180 dias para o texto integral |
| Peças e pareceres gerados | Clientes | Eventos do webhook | Revisão e aprovação | Execução de contrato | 180 dias; o resultado aprovado fica no sistema do cliente |
| Dados de desempenho (Nekt, CRM) | Clientes e, indiretamente, leads | Fonte do cliente, lidos como agregados | Baselines e metas | Execução de contrato | Não armazenados no portal |
| Dado pessoal de paciente | Pacientes (sensível, art. 11) | **Não deve existir** | Fora de escopo | Não aplicável | Bloqueado na entrada |

**Verificação feita:** busca por padrões de CPF, e-mail, telefone e nome de paciente nos 738 eventos. Todos os acertos eram falsos positivos (trechos de identificadores, um e-mail fictício de exemplo e menções a prontuário em texto de conformidade). A busca é por padrão e não garante ausência total.

## 3. Papéis e fluxo internacional

- **Vanguarda Martech** é operadora dos dados do briefing em nome do cliente (controlador) e controladora dos dados dos próprios analistas.
- **Suboperadores e locais** (a confirmar contratos e regiões):

| Serviço | Função | Local | Situação |
|---|---|---|---|
| Supabase | Banco, autenticação, tempo real | São Paulo (confirmado) | Sem transferência internacional no armazenamento |
| Vercel | Hospedagem do portal | Funções provavelmente fora do Brasil | Confirmar região das funções e contrato |
| CrewAI AMP | Execução dos agentes | Provavelmente exterior | Confirmar contrato, retenção e uso de dados para treino |
| Provedor do modelo de linguagem | Geração de texto | Provavelmente exterior | Confirmar quem é, região e política de retenção |
| Nekt | Dados de desempenho | A confirmar | Dados agregados |

- **Transferência internacional (arts. 33 a 36):** exige mecanismo válido. Hoje não há registro de qual. Caminho recomendado: cláusulas-padrão da ANPD ou contratos que já as incorporem. Validar com o jurídico.
- **Contrato com o cliente:** incluir autorização expressa ao uso de IA no processamento, a lista de suboperadores e a regra de que o briefing não contém dado pessoal.

## 4. Controles existentes

- Decisão humana obrigatória em G1, G2 e G3, cada portão restrito aos aprovadores designados. Atende ao espírito do art. 20 (revisão humana).
- Publicação desligada: nada sai para canal externo.
- Acesso por convite; quem não está em convites não vê nada. Políticas de leitura em tempo real exigem perfil.
- Chave de serviço somente no servidor; verificações de papel em todas as rotas de escrita.
- Auditoria com nome, sessão, data, hora e o que mudou; exportação em CSV restrita a aprovador e administrador.
- Webhook autenticado por segredo compartilhado.
- Região do banco em São Paulo.

## 5. Achados de segurança

| # | Achado | Severidade | Tratamento | Status |
|---|---|---|---|---|
| S1 | Sem cabeçalhos de segurança no portal (HSTS, X-Frame-Options, nosniff, política de referência, permissões) | Média | Configurados em `next.config.mjs`; política de conteúdo (CSP) em modo de relatório | No PR |
| S2 | Privilégios de tabela concedidos a anon e authenticated, contidos só por RLS sem política | Média | `seguranca_lgpd.sql`, bloco 1 | No PR, a aplicar |
| S3 | Função de papel executável por anon | Baixa | `seguranca_lgpd.sql`, bloco 2 | No PR, a aplicar |
| S4 | Auditoria não é imutável no banco | Média | Gatilho que bloqueia alteração e exclusão, bloco 3 | No PR, a aplicar |
| S5 | Proteção contra senhas vazadas desligada no Supabase Auth | Média | Ativar no painel do Supabase | Pendente (administradora) |
| S6 | Sem segundo fator e um único administrador | Alta para o administrador | Ativar MFA para administrador e aprovadores; cadastrar um segundo administrador de contingência | Pendente |
| S7 | Webhook: comparação de segredo não é de tempo constante; segredo aceito na URL; sem limite de tamanho | Média | Aceitar só cabeçalho, comparar em tempo constante, limitar corpo, rotacionar o segredo | Pendente (função de borda) |
| S8 | Sem limite diário de disparos; cada disparo consome tokens | Baixa | Limite por usuário e por dia na rota de disparo | Pendente |
| S9 | Eventos guardam texto integral sem prazo | Média (LGPD) | Função de expurgo de 180 dias, bloco 4 | No PR, a agendar |
| S10 | Dado pessoal poderia entrar pelo briefing | Média | Bloqueio de CPF válido, e-mail, telefone, nome de paciente e prontuário antes do disparo | No PR |
| S11 | Backup e recuperação não verificados | A confirmar | Confirmar o plano do Supabase e testar uma restauração | Pendente |

## 6. Compliance do conteúdo (saúde)

- O Guardião verifica claims, termos proibidos, CDC e CONAR, e o G2 repete a revisão. Ele varia entre rodadas: aprovou e reprovou a mesma expressão ("excelência médica") em pilotos diferentes.
- **Regra para o piloto:** todo conteúdo de saúde exige aval do responsável técnico do cliente antes de qualquer publicação. A publicação segue desligada. O analista aprova a **qualidade da peça**, não a conformidade regulatória (Resolução CFM 2.336/2023, CDC, CONAR). A conformidade fica registrada como pendência com o marcador padrão [VALIDAR MÉDICO].
- Confirmar com o jurídico a exigência de identificar conteúdo gerado por IA em cada canal.

## 7. Matriz de riscos

| Risco | Probabilidade | Impacto | Mitigação | Dono |
|---|---|---|---|---|
| Dado pessoal em briefing ou peça | Média | Alto | Bloqueio na entrada, orientação, varredura periódica | Head de IA |
| Transferência internacional sem mecanismo | Alta | Alto | Contratos e cláusulas-padrão antes do piloto com cliente real | Jurídico |
| Aprovação de superlativo em saúde | Média | Alto | Aval do responsável técnico, publicação desligada | Aprovadores |
| Acesso indevido ao portal | Baixa | Alto | Convite, MFA, privilégios mínimos, auditoria | Head de IA |
| Vazamento do segredo do webhook | Baixa | Médio | Rotação e comparação segura | Head de IA |
| Custo descontrolado de tokens | Média | Médio | Limite diário, tela de ROI | Head de IA |
| Perda de dados | Baixa | Alto | Backup e teste de restauração | Head de IA |

## 8. Plano de ação e responsabilidades

| Ação | Responsável | Apoio | Prazo |
|---|---|---|---|
| Merge do PR com cabeçalhos, bloqueio de dados pessoais e SQL de endurecimento | Head de IA | Claude | D1 |
| Aplicar `seguranca_lgpd.sql` | Head de IA | Claude | D1 |
| Ativar proteção contra senha vazada e MFA; segundo administrador | Head de IA | Mauro, Jéssica | D1 |
| Rotacionar segredo do webhook e endurecer a função | Head de IA | Claude | D2 |
| Designar encarregado (DPO) e publicar o canal do titular | Diretoria | Jurídico | D3 |
| Registro das operações de tratamento (art. 37) e RIPD (art. 38) | Encarregado | Head de IA | D5 |
| Contratos: operador e suboperadores, transferência internacional | Jurídico | Head de IA | D7 |
| Aviso de privacidade e termo de conduta dos analistas | Jurídico | RH | D3 |
| Plano de resposta a incidentes testado | Head de IA | Encarregado | D5 |
| Política de retenção aprovada e agendamento do expurgo | Encarregado | Head de IA | D5 |

## 9. Condições de liberação (go/no-go)

**Obrigatórias antes do primeiro analista:**
1. PR de segurança mesclado e SQL aplicado.
2. MFA ativo para administrador e aprovadores; segundo administrador cadastrado.
3. Proteção contra senha vazada ligada.
4. Segredo do webhook rotacionado.
5. Encarregado designado e aviso de privacidade interno entregue.
6. Termo de conduta assinado pelos analistas: sem dado pessoal no briefing, sem copiar conteúdo para fora do portal, sem compartilhar acesso.
7. Piloto restrito a clientes sem dado sensível no briefing ou com contrato de operador já assinado.
8. Publicação confirmada desligada.

**Obrigatórias antes de cliente real em produção:** RIPD concluído, contratos com suboperadores e mecanismo de transferência internacional, retenção aprovada e agendada, teste de restauração de backup.

## 10. Resposta a incidentes

1. Quem percebe avisa a Head de IA e o encarregado na hora.
2. Conter: revogar acesso do usuário, rotacionar segredos, desligar disparos.
3. Registrar: o que, quando, quais dados, quais titulares (a auditoria e os eventos ajudam).
4. Avaliar risco ao titular. Se relevante, o controlador comunica a ANPD e os titulares nos prazos da regulamentação vigente (a regra atual fala em três dias úteis; confirmar a resolução em vigor com o jurídico).
5. Aprender: causa raiz e ação preventiva em até 10 dias úteis.

## 11. Indicadores do piloto

- Dados pessoais barrados na entrada (meta: acompanhar, esperado zero).
- Acessos por pessoa e por portão; decisões sem justificativa.
- Alertas de qualidade por execução.
- Pedidos de titular recebidos e prazo de resposta.
- Custo por campanha.

## 12. Varredura completa de 07/10/2026

| # | Achado | Gravidade | Tratamento | Situação |
|---|---|---|---|---|
| V1 | Next.js 14.2.15 com vulnerabilidades críticas conhecidas (execução remota de código no otimizador de imagens, desvio de autorização no middleware, SSRF, negação de serviço) e postcss vulnerável | Crítica | Atualização para Next.js 15.5.27 e postcss 8.5.29 por sobreposição; `npm audit` de produção com 0 vulnerabilidades | Corrigido |
| V2 | Webhook sem comparação de segredo em tempo constante, sem teto de corpo e com erro de banco devolvido ao chamador | Média | Função `crewai-webhook` v4: comparação em tempo constante, teto de 2 MB, erros genéricos. O segredo na URL fica, porque a CrewAI AMP não envia cabeçalho nos webhooks de tarefa | Corrigido; caminho autenticado a confirmar no próximo piloto |
| V3 | Sem teto de tamanho nos textos enviados aos agentes e sem limite diário de disparos | Média | Tetos por campo (1.500 e 3.000), feedback de 4.000 e limite de 10 disparos por pessoa em 24 horas, ajustável em Administração | Corrigido |
| V4 | Chamadas que alteram estado sem checagem de origem | Média | Rejeição de `Origin` diferente do portal nas rotas de API | Corrigido |
| V5 | Dado pessoal podia entrar pela base de conhecimento | Média | Bloqueio de CPF válido, nome de paciente e prontuário ao salvar (contatos institucionais continuam permitidos) | Corrigido |
| V6 | API devolvia texto técnico da plataforma ao usuário em caso de recusa | Baixa | Mensagem genérica; o detalhe fica gravado no banco | Corrigido |
| V7 | Revisão final do G2 sem parecer da direção de arte; rubrica e auditoria de mídia apareciam como se fossem da versão final; alerta falso de "faltam linhas RESUMO" por nota escalada (90/90) | Média | Trava de cobertura das cinco entregas, nota de versão inicial acrescentada por código e nota com denominador escalado aceita | Corrigido na crew; exige redeploy na AMP |
| V8 | Falta de guia de uso para os analistas | Média | Guia em `docs/guia-do-analista.md` e página `/guia` no portal | Corrigido; campos a preencher |
| V9 | Estado compartilhado em memória na crew (contexto do cliente e feedback por portão) | Média | O portal só permite uma campanha por vez. **Não disparar campanha pelo painel da AMP enquanto outra roda**, para não misturar clientes | Mitigado por procedimento |
| V10 | Proteção contra senha vazada, segundo fator e segundo administrador | Alta | Configuração no painel do Supabase | Pendente (administradora) |
| V11 | Expurgo de eventos de 180 dias não criado | Média | Bloco 4 de `seguranca_lgpd.sql` | Pendente (administradora) |
| V12 | Provedor do modelo de linguagem, região da CrewAI AMP e da Vercel, contratos e transferência internacional | Alta | Confirmação com fornecedores e jurídico | Pendente |
| V13 | Papel `app_head` com todos os privilégios nas tabelas | A confirmar | Confirmar a quem pertence | Pendente |

**Verificado e sem achado:** sem segredo no repositório nem no histórico do código da crew; arquivos `.env` fora do controle de versão; nenhuma chamada de execução de comando, desserialização insegura ou leitura de caminho controlado pelo usuário na crew; a ferramenta de publicação nasce desligada; a ferramenta de guia de marca usa nome normalizado e só lê pastas listadas.

| V14 | Setup de IA do VJOB (L3 confidencial na Nekt) passa a seguir para os agentes | Média | Cópia só no Supabase (sem acesso do navegador), nunca no repositório público; checagem de dado pessoal antes de sincronizar; listas negativas fora do texto permitido. Depende da validação dos fornecedores do modelo | Tratado; ver `nekt-vjob-setup.md` |
