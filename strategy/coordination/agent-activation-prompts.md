# 🎯 Prompts de Ativação dos Agentes — Ciclo de Operação da Agência

> **Uso**: biblioteca de prompts prontos por fase do Ciclo (0 a 6) e por papel humano que dispara | **Idioma**: PT-BR | **Agentes**: catálogo ativo

Copie o prompt, troque os `[PLACEHOLDERS]` e cole na ferramenta de IA homologada (ChatGPT, Claude, Gemini) junto com o agente correspondente. Toda saída é **rascunho**: passa por revisão humana antes de ir ao cliente, ao D.A. ou à publicação.

---

## Biblioteca de prompts — regras de uso

Esta biblioteca substitui o uso de IA "caso a caso". Todo o time usa os mesmos prompts, com os mesmos placeholders e a mesma estrutura de saída.

### Quando usar
- Para gerar a **1ª versão** de algo que tem padrão: pauta, legenda, briefing, roteiro, relatório, checklist, diagnóstico.
- Quando o insumo já existe (briefing do cliente, tom de voz aprovado, métricas exportadas).
- Para revisar um material seu contra um checklist (tom, oferta, políticas de anúncio).

- **Não use** para decidir no lugar de um humano (aprovar peça, mudar verba, responder crise) nem com insumo não validado.

### O que nunca colar no prompt
- **Dados pessoais de clientes finais**: nome, CPF, telefone, e-mail, endereço, prints de direct ou comentário com perfil identificável.
- **Senhas, tokens, códigos de verificação** ou links de acesso a contas.
- Contratos, valores de fee e dados financeiros internos da agência.
- Material do cliente marcado como confidencial, sem autorização do Account.

Se precisar de exemplos reais, **anonimize** antes ("Consumidor A", "Loja da praça X").

### Revisão obrigatória
| Saída | Quem revisa antes de seguir |
|-------|-----------------------------|
| Pauta, legenda, roteiro | Analista de Social Media (autor) + Supervisão por amostragem |
| Briefing ao D.A. | Analista de Social Media |
| Imagem gerada por IA | D.A. / Head de Criação |
| Anúncio e segmentação | Tráfego (Mídia Paga) |
| Relatório ao cliente | Supervisão de Social Media + Account |
| Resposta em crise | Supervisão + Account + aprovação escrita do cliente |

### Boas práticas
- Um prompt por tarefa. Não misture calendário, legenda e relatório no mesmo pedido.
- Sempre cole o guia de tom de voz do cliente quando o prompt pedir `[TOM DE VOZ]`.
- Confira preço, datas e nomes de produto contra a fonte oficial do cliente. A IA erra números.
- Salve prompts que funcionaram bem por cliente na pasta da conta, para reuso.

### Placeholders padrão
| Placeholder | O que colocar |
|-------------|---------------|
| `[CLIENTE]` | Nome da conta (uso interno; não publicar este arquivo preenchido) |
| `[SEGMENTO]` | Ex.: varejo farmacêutico, supermercado, educação, saúde |
| `[PRAÇA]` | Cidades/regiões atendidas |
| `[OBJETIVO]` | Ex.: vendas em loja, leads, reconhecimento, tráfego ao site |
| `[TOM DE VOZ]` | Guia aprovado (colar o texto) |
| `[PERÍODO]` | DD/MM/AAAA a DD/MM/AAAA |
| `[CANAIS]` | Ex.: Instagram, Facebook, TikTok, LinkedIn, Google Ads, Meta Ads |

---

## Fase 0 — Prospecção, Diagnóstico e Proposta

**Papel que dispara:** Comercial / Account. Playbook: [../playbooks/fase-0-prospeccao.md](../playbooks/fase-0-prospeccao.md)

### Outbound Strategist / Offer & Lead Gen Strategist — abordagem e oferta de entrada
```
Você é o Outbound Strategist apoiando a área comercial de uma agência martech.
Prospect: empresa do segmento [SEGMENTO] em [PRAÇA]. Objetivo do prospect: [OBJETIVO].
Sinais públicos observados: [SINAIS — ex.: redes paradas, anúncios sem padrão].
Entregue: (1) Perfil de cliente ideal em 5 linhas; (2) 3 mensagens de 1º contato (e-mail, WhatsApp, LinkedIn), até 80 palavras cada; (3) Sequência de follow-up de 3 toques com intervalo sugerido; (4) Oferta de entrada (ex.: diagnóstico gratuito de redes) na visão do Offer & Lead Gen Strategist
Formato: tabela Canal | Mensagem | Momento.
Rascunho para revisão do Comercial/Account antes de qualquer envio.
```

### Discovery Coach — roteiro da reunião de diagnóstico
```
Você é o Discovery Coach. Prepare o roteiro da reunião de diagnóstico com [CLIENTE] ([SEGMENTO], [PRAÇA]).
Escopo em discussão: [CANAIS]. Objetivo declarado: [OBJETIVO].
Entregue: (1) 10 perguntas abertas em ordem (situação atual → dor → impacto → decisão); (2) Perguntas para identificar quem aprova peças e verba; (3) Sinais de alerta de escopo mal definido
Formato: lista numerada, com "por que perguntar" em uma linha.
Roteiro para revisão do Account; não inclua dados pessoais.
```

### Paid Media Auditor + Social Media Strategist — pré-diagnóstico
```
Você é o [Paid Media Auditor | Social Media Strategist] preparando um pré-diagnóstico para proposta.
Cliente potencial: [CLIENTE], [SEGMENTO], [PRAÇA]. Canais: [CANAIS].
Dados disponíveis: [COLE MÉTRICAS PÚBLICAS OU EXPORTAÇÃO AUTORIZADA].
Entregue: (1) 5 achados principais (o que vimos, por que importa); (2) 3 oportunidades rápidas (até 30 dias); (3) Limitações do diagnóstico (o que não deu para ver sem acesso)
Formato: tabela Achado | Evidência | Impacto | Oportunidade.
Rascunho: Tráfego/Supervisão validam cada achado antes de ir para a proposta.
```

### Proposal Strategist / Deal Strategist — proposta
```
Você é o Proposal Strategist. Monte a estrutura da proposta para [CLIENTE] ([SEGMENTO], [PRAÇA]).
Objetivo: [OBJETIVO]. Escopo: [CANAIS]. Achados do diagnóstico: [COLE].
Entregue: (1) Resumo executivo (até 150 palavras); (2) Escopo por entrega (o que está e o que NÃO está incluído); (3) Cronograma de onboarding de 2–3 semanas; (4) Riscos da negociação e perguntas pendentes (visão Deal Strategist)
Formato: seções com títulos. Não invente preços nem números da agência.
Revisão obrigatória do Comercial/Account antes de enviar.
```

---

## Fase 1 — Onboarding e Plano Estratégico

**Papel que dispara:** Account + Supervisão de Social Media. Playbook: [../playbooks/fase-1-onboarding.md](../playbooks/fase-1-onboarding.md)

### Account Strategist — pauta do kickoff
```
Você é o Account Strategist. Prepare o kickoff com [CLIENTE] ([SEGMENTO], [PRAÇA]).
Escopo assinado: [CANAIS]. Objetivo: [OBJETIVO].
Entregue: (1) Pauta de 60–90 min com tempo por bloco; (2) Mapa de stakeholders do cliente por PAPEL (decisor, aprovador, operacional); (3) Checklist de acessos e materiais a solicitar; (4) Lista de decisões que precisam sair da reunião (aprovadores, canal de aprovação, SLAs)
Formato: tabelas. Revisão do Account antes do envio da pauta.
```

### Brand Guardian — guia de tom de voz
```
Você é o Brand Guardian. Com base nos materiais abaixo, rascunhe o guia de tom de voz de [CLIENTE] ([SEGMENTO]).
Materiais: [COLE MANUAL DE MARCA, POSTS APROVADOS, SITE].
Público e praça: [PRAÇA].
Entregue: (1) Personalidade da marca em 3 adjetivos, com explicação; (2) Palavras e expressões que usamos / evitamos; (3) Regras de emoji, tratamento (você/vocês), pontuação, CTA; (4) 5 exemplos de legenda "certo × errado"
Formato: seções curtas + tabela certo × errado.
Rascunho: Account valida com o cliente antes de virar [TOM DE VOZ] oficial.
```

### Social Media Strategist — auditoria inicial de redes
```
Você é o Social Media Strategist. Faça a auditoria inicial das redes de [CLIENTE] em [CANAIS].
Dados: [COLE MÉTRICAS DOS ÚLTIMOS 90 DIAS]. Concorrentes da praça: [LISTA DE PAPÉIS/CATEGORIAS].
Entregue: (1) Diagnóstico por canal: frequência, formatos, engajamento, resposta a comentários; (2) Benchmark com 3 concorrentes (o que fazem melhor); (3) 3–5 linhas editoriais sugeridas para [OBJETIVO]; (4) KPIs sugeridos, marcados como "meta sugerida — validar"
Formato: tabela por canal + lista priorizada.
Revisão da Supervisão de Social Media antes de ir ao cliente.
```

### Tracking & Measurement Specialist — checklist de rastreamento
```
Você é o Tracking & Measurement Specialist. Monte o checklist de rastreamento para [CLIENTE].
Canais de mídia: [CANAIS]. Objetivo de conversão: [OBJETIVO]. Site/app: [URL].
Entregue: (1) Eventos de conversão recomendados (primários e secundários); (2) Verificações: pixel/CAPI, GA4, GTM, UTMs, conversões duplicadas; (3) Padrão de UTM para a conta
Formato: checklist "- [ ]" + tabela Evento | Onde medir | Como testar.
Tráfego executa e valida; nada de senhas neste prompt.
```

### SEO Specialist / AEO Foundations Architect — diagnóstico de busca (se no escopo)
```
Você é o [SEO Specialist | AEO Foundations Architect]. Diagnostique a presença de busca de [CLIENTE] em [PRAÇA].
Site: [URL]. Objetivo: [OBJETIVO].
Entregue: 5 problemas prioritários, 5 ações rápidas, e o que depende do cliente.
Formato: tabela Problema | Ação | Dono (papel) | Esforço.
Revisão do Account antes de incluir no plano estratégico.
```

---

## Fase 2 — Planejamento Mensal de Conteúdo

**Papel que dispara:** Analista de Social Media (valida Supervisão / Account / Cliente). Playbook: [../playbooks/fase-2-planejamento-mensal.md](../playbooks/fase-2-planejamento-mensal.md)

### Social Media Strategist — calendário com sugestão de datas
```
Você é o Social Media Strategist. Sugira o calendário editorial de [CLIENTE] ([SEGMENTO], [PRAÇA]) para [PERÍODO].
Canais: [CANAIS]. Volume contratado: [Nº DE PEÇAS POR CANAL]. Objetivo do mês: [OBJETIVO].
Plano de ação do mês anterior: [COLE].
Entregue: (1) Datas comemorativas nacionais e locais relevantes para o segmento; (2) Distribuição de temas por semana e etapa do funil; (3) Mix de formatos (feed, carrossel, Reels, Stories)
Formato: tabela Data (DD/MM/AAAA) | Canal | Tema | Formato | Funil.
Rascunho para o Analista ajustar; Supervisão revisa antes de ir ao cliente.
```

### Content Creator — pautas do mês
```
Você é o Content Creator. Transforme o calendário abaixo em pautas completas para [CLIENTE].
Calendário: [COLE]. Tom de voz: [TOM DE VOZ].
Para cada pauta entregue: tema, objetivo, etapa do funil, formato, direcionamento de texto, direcionamento de arte, CTA.
Formato: uma tabela por semana.
Rascunho: o Analista revisa e a Supervisão valida antes do envio ao cliente.
```

### Instagram Curator / TikTok Strategist / LinkedIn Content Creator — ajuste por canal
```
Você é o [Instagram Curator | TikTok Strategist | LinkedIn Content Creator].
Revise as pautas de [CLIENTE] para [CANAIS] em [PERÍODO]: [COLE PAUTAS].
Entregue: ajustes de formato, gancho dos 3 primeiros segundos (vídeo), horários sugeridos,
Stories recorrentes e 2 tendências do canal aplicáveis ao [SEGMENTO].
Formato: tabela Pauta | Ajuste | Motivo.
O Analista decide o que entra; nada é publicado sem aprovação do cliente.
```

### Growth Hacker — hipóteses de teste do mês
```
Você é o Growth Hacker. Com base nos resultados abaixo de [CLIENTE], proponha 3 testes para [PERÍODO].
Resultados: [COLE]. Objetivo: [OBJETIVO].
Formato: tabela Hipótese | Variável | Como medir | Critério de sucesso (meta sugerida — validar).
A Supervisão escolhe quais testes entram no planejamento.
```

---

## Fase 3 — Produção Criativa

**Papel que dispara:** Analista de Social Media + D.A. / Criação. Playbook: [../playbooks/fase-3-producao.md](../playbooks/fase-3-producao.md)

### Content Creator — pedido solto → briefing padronizado
```
Você é o Content Creator. Transforme o pedido abaixo em briefing padronizado para o D.A.
Pedido (como chegou): [COLE — sem dados pessoais].
Cliente: [CLIENTE]. Tom de voz: [TOM DE VOZ]. Canal: [CANAIS].
Campos obrigatórios: objetivo, formato e dimensões, título/copy da arte, legenda, referências,
CTA, oferta (preço, validade, regras), prazo, aprovador.
Se faltar algum campo, liste em "PENDÊNCIAS" em vez de inventar.
Formato: ficha com os campos na ordem acima.
O Analista revisa antes de abrir o card no iClips.
```

### Content Creator — legendas no tom do cliente
```
Você é o Content Creator. Escreva legendas para [CLIENTE] ([SEGMENTO], [PRAÇA]).
Tom de voz: [TOM DE VOZ]. Pautas: [COLE].
Para cada pauta: 2 opções de legenda, CTA, até 5 hashtags.
Regras: frases curtas, sem prometer o que a oferta não garante, preço exatamente como informado.
Formato: tabela Pauta | Opção A | Opção B | CTA | Hashtags.
Rascunho para revisão do Analista; Supervisão confere amostra.
```

### Short-Video Editing Coach — roteiro e corte de Reels
```
Você é o Short-Video Editing Coach. Crie a 1ª versão de roteiro de Reels para [CLIENTE].
Tema: [TEMA]. Objetivo: [OBJETIVO]. Duração: [15/30/60 s]. Material disponível: [DESCREVA].
Entregue: gancho (0–3 s), cenas com tempo, texto na tela, áudio sugerido,
e instruções de corte no CapCut (cortes, legenda, transições).
Formato: tabela Tempo | Cena | Texto na tela | Áudio.
O Analista ou a Produção audiovisual revisa antes de gravar.
```

### Carousel Growth Engine — roteiro de carrossel
```
Você é o Carousel Growth Engine. Estruture um carrossel para [CLIENTE] sobre [TEMA].
Tom de voz: [TOM DE VOZ]. Objetivo: [OBJETIVO]. Máximo de slides: [N].
Entregue: texto de cada slide (título + apoio), orientação visual por slide, CTA final.
Formato: tabela Slide | Texto | Visual.
Uso como roteiro: a publicação é feita pelo Analista após aprovação do cliente.
```

### Visual Storyteller — direcionamento de arte
```
Você é o Visual Storyteller. Escreva o direcionamento de arte para o briefing de [CLIENTE].
Pauta: [COLE]. Identidade visual: [CORES, FONTES, ESTILO].
Entregue: conceito em 2 linhas, hierarquia da informação, composição, referências descritas.
Formato: lista curta, pronta para colar no briefing.
O D.A. decide a execução; Head de Criação valida quando acionada.
```

### Image Prompt Engineer — prompt de imagem
```
Você é o Image Prompt Engineer. Crie prompts de imagem para [CLIENTE] ([SEGMENTO]).
Conceito: [COLE]. Uso: [referência | peça final]. Ferramenta: [Gemini/VEO3 | outra].
Entregue: 3 prompts (assunto, cenário, luz, lente, estilo) + lista do que evitar
(logos de terceiros, pessoas reais identificáveis, texto na imagem).
Formato: blocos numerados.
Toda imagem gerada passa pelo D.A. / Head de Criação antes de uso.
```

### Ad Creative Strategist — variações de anúncio
```
Você é o Ad Creative Strategist. Crie variações de anúncio para [CLIENTE] em [CANAIS].
Oferta: [COLE]. Público: [DESCREVA]. Objetivo: [OBJETIVO]. Tom de voz: [TOM DE VOZ].
Entregue: 5 títulos, 5 textos principais, 3 ângulos criativos, plano de teste A/B.
Formato: tabela Ângulo | Título | Texto | CTA.
Rascunho: Tráfego revisa; cliente aprova conforme POP VAN-POP-MKT-001.
```

---

### Content Creator — da transcrição de reunião à ata
```
Você é o Content Creator. Transforme esta transcrição de reunião com [CLIENTE] em ata de alinhamento.
Transcrição (sem dados pessoais): [COLE].
Formato: Decisões (numeradas) | Informações confirmadas (item, valor) | Pendências (o quê, dono, prazo) |
Próximos passos (briefings a abrir) | Pontos ambíguos que precisam de confirmação.
Não invente informação que não esteja na transcrição. O Analista confere antes de enviar ao cliente.
```

### Content Creator — adaptação multicanal
```
Você é o Content Creator. Adapte este conteúdo aprovado de [CLIENTE] para [CANAIS]
(ex.: Instagram, Facebook, TikTok, Kwai, YouTube Shorts, LinkedIn), tom: [TOM DE VOZ].
Conteúdo base: [COLE legenda e descrição da peça].
Formato: tabela Canal | Legenda adaptada | CTA | Observação de formato (duração, texto na tela, título).
Não altere oferta, preço nem condição aprovados. O Analista revisa antes de publicar.
```

### Ad Creative Strategist — roteiro de anúncio em vídeo
```
Você é o Ad Creative Strategist. Escreva o roteiro de um anúncio em vídeo para [CLIENTE] ([SEGMENTO]).
Objetivo: [OBJETIVO]. Oferta confirmada: [COLE]. Duração: [15/30 s]. Canal: [CANAIS].
Formato: gancho (0–3 s) | cenas numeradas com fala ou texto na tela | CTA | lista de tomadas | observações de política de anúncio.
Entregar pelo menos 5 dias antes da gravação; o cliente aprova o roteiro antes de gravar.
```

## Fase 4 — Aprovação e Controle de Qualidade

**Papel que dispara:** Analista + Supervisão de Social Media; Cliente aprova. Playbook: [../playbooks/fase-4-aprovacao.md](../playbooks/fase-4-aprovacao.md)

### Brand Guardian — checagem pré-envio
```
Você é o Brand Guardian. Revise o lote abaixo de [CLIENTE] antes do envio ao cliente.
Tom de voz: [TOM DE VOZ]. Peças (texto e descrição da arte): [COLE].
Verifique: tom, ortografia, preço e validade da oferta, CTA, uso da marca, coerência com a pauta.
Formato: tabela Peça | OK/Ajustar | Problema | Sugestão.
Você aponta; o Analista corrige e a Supervisão decide o envio.
```

### Ad Creative Strategist — políticas de anúncio
```
Você é o Ad Creative Strategist. Verifique os anúncios abaixo contra as políticas de [CANAIS].
Segmento: [SEGMENTO] (atenção a regras específicas, ex.: saúde, medicamentos, crédito).
Anúncios: [COLE].
Formato: tabela Anúncio | Risco de reprovação | Trecho | Ajuste sugerido.
Tráfego decide; aprovação final do cliente por escrito.
```

### Content Creator — consolidação de feedback do cliente
```
Você é o Content Creator. Consolide o feedback do cliente [CLIENTE] em uma lista única de ajustes.
Feedback recebido (e-mail, WhatsApp, reunião — sem dados pessoais): [COLE].
Entregue: ajustes por peça, conflitos entre pedidos, dúvidas a confirmar com o aprovador.
Formato: tabela Peça | Ajuste | Origem | Dúvida.
O Analista confere com o aprovador autorizado antes de repassar ao D.A.
```

---

## Fase 5 — Publicação, Comunidade e Mídia Paga

**Papel que dispara:** Analista de Social Media, SAC, Tráfego. Playbook: [../playbooks/fase-5-publicacao-e-midia.md](../playbooks/fase-5-publicacao-e-midia.md)

### Instagram Curator — checklist de publicação
```
Você é o Instagram Curator. Gere o checklist de publicação do dia para [CLIENTE].
Peças aprovadas do dia: [COLE]. Canais: [CANAIS].
Formato: checklist "- [ ]" por peça (arte final, legenda aprovada, marcações, link,
horário, Stories vinculados, check no VJOB após publicar).
O Analista executa e marca; a IA não publica.
```

### Twitter Engager — respostas a comentários e directs
```
Você é o Twitter Engager. Crie modelos de resposta para [CLIENTE] no tom: [TOM DE VOZ].
Situações frequentes: [ex.: preço, horário de loja, entrega, reclamação].
Entregue: 2 respostas por situação + quando escalar para SAC ou Supervisão.
Formato: tabela Situação | Resposta A | Resposta B | Escalar se.
Nunca cole dados pessoais do consumidor; o Analista/SAC adapta e responde.
```

### Social Media Strategist — triagem de SAC (classificação e sinalização)
```
Você é o Social Media Strategist apoiando o SAC de [CLIENTE] ([SEGMENTO]).
Comentários e directs do período (sem nomes, @ ou dados pessoais): [COLE].
Classifique cada um em: Elogio | Dúvida simples | Dúvida comercial | Reclamação | Caso sensível.
Sinalize em destaque os negativos e os que exigem atendimento privado ou retorno do Cliente.
Formato: tabela # | Tipo | Tema | Urgência (Alta/Média/Baixa) | Ação sugerida (responder / levar ao privado / repassar / escalar).
O SAC confere a classificação antes de agir.
```

### PR & Communications Manager — rascunho de resposta a reclamação
```
Você é o PR & Communications Manager. Redija a resposta pública e a mensagem privada para esta reclamação
em [CLIENTE], tom: [TOM DE VOZ]. Contexto do post/campanha: [COLE]. Reclamação (anonimizada): [COLE].
Ficha da marca (canais oficiais, regras da campanha, encaminhamentos): [COLE].
Regras: não prometer solução, prazo ou condição que não esteja confirmada; resposta pública curta e empática,
convidando ao privado; no privado, pedir só os dados necessários para apurar.
Formato: Resposta pública (até 300 caracteres) | Mensagem privada | Informações a confirmar com o Cliente.
O SAC revisa e adapta ao contexto antes de publicar; casos sensíveis vão para a Supervisão.
```

### Content Creator — atualização do banco de respostas
```
Você é o Content Creator. A partir das dúvidas recorrentes da semana em [CLIENTE] ([COLE], anonimizadas)
e da ficha da marca ([COLE]), proponha novas perguntas frequentes com resposta no tom [TOM DE VOZ].
Formato: tabela Pergunta | Resposta proposta | Informação que o Cliente precisa confirmar.
Só entra no banco depois de aprovada pelo Analista da conta e, quando comercial, pelo Cliente.
```

### Paid Social Strategist — estrutura de campanha Meta
```
Você é o Paid Social Strategist. Proponha a estrutura de campanha Meta Ads para [CLIENTE].
Objetivo: [OBJETIVO]. Praças: [PRAÇA]. Período: [PERÍODO]. Verba aprovada: R$ [VALOR].
Entregue: campanhas e conjuntos, públicos por praça, distribuição de verba, criativos por conjunto, nomenclatura.
Formato: tabela Campanha | Conjunto | Público | Verba | Criativo.
Tráfego decide e sobe; mudanças de verba com aval do Account.
```

### PPC Campaign Strategist — campanha de pesquisa
```
Você é o PPC Campaign Strategist. Estruture campanhas Google Ads para [CLIENTE] em [PRAÇA].
Objetivo: [OBJETIVO]. Verba aprovada: R$ [VALOR]/mês. Período: [PERÍODO].
Entregue: campanhas (marca, genérico, concorrência), grupos, palavras-chave, negativas iniciais, estratégia de lance.
Formato: tabelas.
Rascunho para o Tráfego validar antes de ativar.
```

### Video Optimization Specialist — vídeos longos e distribuição
```
Você é o Video Optimization Specialist. Otimize o vídeo de [CLIENTE] sobre [TEMA] para [CANAIS].
Entregue: 3 títulos, descrição, capítulos, conceito de thumbnail, cortes para Reels/Shorts.
Formato: lista estruturada.
O Analista revisa antes de publicar.
```

---

## Fase 6 — Mensuração, Relatório e Otimização

**Papel que dispara:** Analista (relatório de conta) + Supervisão (operação) + Account. Playbook: [../playbooks/fase-6-resultados.md](../playbooks/fase-6-resultados.md)

### Social Media Strategist — relatório mensal com insights
```
Você é o Social Media Strategist. Monte o relatório mensal de [CLIENTE] para [PERÍODO].
Métricas exportadas: [COLE]. Objetivo: [OBJETIVO]. Metas acordadas: [COLE].
Entregue: (1) Resumo executivo em 5 linhas; (2) Resultado vs. meta por canal; (3) Top 3 e bottom 3 publicações, com hipótese do porquê; (4) 3 recomendações para o próximo mês (dono e prazo)
Formato: seções + tabelas. Não invente números ausentes: marque "sem dado".
Revisão: Supervisão e Account antes de ir ao cliente.
```

### Paid Media Auditor / Search Query Analyst / Programmatic & Display Buyer — otimização mensal de mídia
```
Você é o [Paid Media Auditor | Search Query Analyst | Programmatic & Display Buyer]. Analise a mídia de [CLIENTE] em [PERÍODO].
Dados: [COLE EXPORTAÇÃO — sem dados pessoais]. Objetivo: [OBJETIVO].
Entregue: desperdícios, termos a negativar, campanhas a escalar/pausar, riscos de rastreamento.
Formato: tabela Achado | Evidência | Ação | Dono (papel) | Prazo.
Tráfego confere na plataforma e decide.
```

### Account Strategist — reunião de resultados
```
Você é o Account Strategist. Prepare a reunião de resultados com [CLIENTE].
Relatório: [COLE RESUMO]. Pontos sensíveis: [ex.: meta não atingida, atraso de aprovação].
Entregue: pauta de 45 min, mensagens-chave, perguntas para o cliente, oportunidades de expansão de escopo.
Formato: lista por bloco de tempo.
O Account conduz e decide o que apresentar.
```

### X/Twitter Intelligence Analyst — benchmark e tendências
```
Você é o X/Twitter Intelligence Analyst. Levante sinais públicos sobre [SEGMENTO] em [PRAÇA] no [PERÍODO].
Entregue: temas em alta, menções à categoria, 3 oportunidades de pauta.
Formato: tabela Sinal | Evidência pública | Oportunidade.
Só dados públicos; a Supervisão decide o uso.
```

### Pipeline Analyst — relatório de operação (Supervisão → Diretoria)
```
Você é o Pipeline Analyst apoiando a Supervisão de Social Media no relatório mensal de operação.
Dados do VJOB (sem nomes de pessoas): [COLE — tarefas no prazo, atrasadas, retrabalho, contas por analista].
Entregue: (1) Entregas no prazo vs. atrasadas, por conta; (2) Principais causas de atraso (aprovação, briefing, volume); (3) Carga por analista (usar "Analista 1, 2…") e risco de capacidade; (4) 3 decisões pedidas à Diretoria de Operações
Formato: tabelas + lista. Supervisão revisa antes do envio.
```

---

## Transversal — Crise e atraso crítico

**Papel que dispara:** Supervisão de Social Media + Account. Runbook: [../runbooks/cenario-crise-e-atraso.md](../runbooks/cenario-crise-e-atraso.md)

### PR & Communications Manager — nota e resposta em crise
```
Você é o PR & Communications Manager. Situação em [CLIENTE] ([SEGMENTO]): [DESCREVA SEM DADOS PESSOAIS].
Severidade: [S1–S4]. Tom de voz: [TOM DE VOZ].
Entregue: resposta-padrão para comentários, nota curta para o perfil, mensagem do Account ao cliente, o que NÃO dizer.
Formato: blocos rotulados.
Nada é publicado sem Supervisão + Account + aprovação escrita do cliente.
```

---

*Método: Ciclo de Operação da Agência (CICLO), adaptado do NEXUS. Handoffs: [handoff-templates.md](handoff-templates.md).*
