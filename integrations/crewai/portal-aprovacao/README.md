# Portal de aprovação (Next.js na Vercel)

Interface para a equipe validar os portões G1, G2 e G3 do fluxo de marketing no CrewAI. Lê os eventos que o receptor
(Edge Function `crewai-webhook`) grava no Supabase e envia a decisão ao `/resume` da plataforma.

## O que faz
| Tela | Função |
|---|---|
| `/` | Fila de portões pendentes e execuções recentes. |
| `/execucao/[id]` | Pedido do portão, entregas geradas (uma a uma, com o agente responsável) e histórico de decisões. |
| `/agentes` | Equipe de 14 agentes: papel, objetivo, ferramentas, tarefas e atividade (entregas e última execução). |
| `/disparar` | Formulário do briefing (17 campos) com revisão e confirmação de custo. Só aprovador. |
| Decisão | Aprovar, Devolver com ajustes (instruções obrigatórias) ou Reprovar. Só o papel **aprovador** decide. |

## Regras importantes
- **O token do CrewAI nunca vai ao navegador.** A rota `/api/decisao` roda no servidor e monta o `/resume`.
- **O servidor escolhe o portão pendente**; o navegador não envia `taskId`. Um portão só recebe uma decisão.
- **"Aprovar" envia exatamente `Aprovado.`** (único texto que a plataforma trata como liberação). **"Devolver"** envia as
  instruções e a plataforma reexecuta o portão. Correções só chegam à aplicação pelo histórico de devoluções.
- **"Reprovar" não chama a plataforma**: a execução permanece pausada e nada é publicado. Fica registrado.
- Cada decisão grava quem decidiu, quando, o texto e a resposta da plataforma em `portal_decisoes`.

## Papéis
`leitor` (só vê), `revisor` (vê), `aprovador` (decide). Quem tem login mas não tem linha em `portal_perfis` não acessa nada.

## Como publicar na Vercel
1. Aplicar `portal.sql` (nesta pasta) no projeto Supabase (aditivo: cria `portal_perfis` e `portal_decisoes`).
2. Criar usuários em Supabase Auth e uma linha em `portal_perfis` por pessoa (nome e papel).
3. Na Vercel: importar o repositório, **Root Directory = `integrations/crewai/portal-aprovacao`**.
4. Variáveis de ambiente (ver `.env.example`): as públicas do Supabase e, **somente no servidor**,
   `SUPABASE_SERVICE_ROLE_KEY`, `CREWAI_API_URL`, `CREWAI_TOKEN`, `WEBHOOK_BASE`, `WEBHOOK_KEY`, `WEBHOOK_AUTOMACAO`.
5. Antes: **resetar o token do CrewAI** que foi exposto durante os testes e usar o novo.

## Limites conhecidos
- Execuções com várias retomadas são agrupadas por `payload.execution_id`; uma execução sem esse campo aparece sozinha.
- Se a plataforma recusar o `/resume`, a decisão fica gravada como "não enviada" e o portal mostra o erro.
- Não há notificação por e-mail ainda: a equipe precisa abrir a fila.

## Por que fica fora de `marketing-operations/`
O deploy do CrewAI é publicado a partir de `marketing-operations/` (subtree). O portal fica ao lado para não entrar no build da plataforma.

## Acesso por convite (link mágico)
Não há senhas. A pessoa informa o e-mail corporativo, recebe um link do Supabase Auth e entra. No primeiro acesso, o portal
vincula o usuário ao papel definido em `portal_convites` (e-mail, nome, cargo, papel, portões). **Quem não está em
`portal_convites` entra no Auth, mas não vê nada.** A tabela já está carregada com a equipe atual.

| Pessoa | Papel | Portões que decide |
|---|---|---|
| Jussara Cavalcante | aprovador | todos |
| Mauro (estratégia) | aprovador | G1 |
| Luana Rocha (criação) | aprovador | G2 |
| Jéssica Nery (operações) | aprovador | G3 |
| Gabriela Bezerra (social media) | revisor | — |
| João Araújo (mídia paga) | revisor | — |

Para incluir alguém: `insert into portal_convites (email, nome, cargo, papel, portoes) values (...)`.
No Supabase, em Authentication, habilitar o provedor de e-mail com link mágico e incluir a URL do portal em Redirect URLs
(`https://<dominio>/auth/callback`).

## Agentes e disparo
- **Catálogo dos agentes:** `lib/agentes.json` é gerado por `python3 scripts/gerar_dados.py` a partir de `agents.yaml`, `tasks.yaml` e
  `crew.py` (nada digitado à mão). Rode de novo quando a crew mudar.
- **Clientes:** `portal_clientes` (55 guias de marca) é carregada de `knowledge/INDEX.md` pelo mesmo script (`clientes.sql`).
  O `cliente` enviado à crew é sempre o nome oficial da tabela, nunca o texto do navegador.
- **Disparo (`/api/disparo`):** exige aprovador e confirmação explícita de custo (~360 mil tokens por campanha). **Trava de custo:**
  recusa se outra campanha estiver rodando (sem evento de fim, sem portão esperando humano e com evento nos últimos 15 min) ou se
  um disparo do portal feito há menos de 10 min ainda não produziu evento. Cada disparo fica em `portal_disparos`.
- **Retomadas:** cada retomada ganha um `kickoff_id` novo e só o evento de pausa traz o `execution_id`. O portal liga as retomadas
  pelo `novo_kickoff_id` gravado em `portal_decisoes`. Decisões tomadas fora do portal (por API) não têm esse vínculo.

## Login e saída
- `/login`: e-mail e senha, "Manter conectado", "Esqueci minha senha" e, como alternativa, link de acesso por e-mail (o método usado até aqui). O botão
  "Continuar com Google" só aparece com `NEXT_PUBLIC_LOGIN_GOOGLE=true`, depois de ativar o provedor Google no Supabase.
- `/recuperar` e `/definir-senha`: quem entrou só por link cria uma senha pelo e-mail de recuperação (ou pelo atalho "senha" no menu lateral).
- `/saiu`: tela exibida depois de sair (botão ⏻ no menu lateral, que faz POST em `/auth/sair`).
- Acesso continua por convite (`portal_convites`): e-mail sem convite entra no Supabase, mas o portal avisa que falta acesso.
- "Manter conectado" desmarcado encerra a sessão quando o navegador é reaberto (conferido no próprio navegador).
- Supabase > Authentication > URL Configuration: em Redirect URLs use `https://marketing-operationsagents.vercel.app/**`
  (cobre `/auth/callback` e `/auth/callback?next=/definir-senha`).

## Base de conhecimento editável
- `/conhecimento` lista os clientes (filtros: incompletos e alterados no portal); `/conhecimento/<cliente>` abre o editor.
- O guia original continua no repositório (`knowledge/<cliente>/guia_identidade_visual.md`, lido por URL pública). Ao editar, o portal grava a
  versão nova em `portal_conhecimento` (a original fica guardada como versão 0) e é possível **restaurar o original** ou qualquer versão do histórico.
- É possível **acrescentar documentos** (texto colado ou arquivo .md/.txt de até 200 KB; até 20 por cliente) e marcar o guia como completo.
- Quem edita: aprovador e revisor (o leitor só consulta). Edição concorrente: se outra pessoa salvou antes, o portal pede para recarregar.
- No disparo, se o cliente tem edição ou documento acrescentado, o portal envia o texto efetivo em `contexto_cliente` (limite de 10.000 caracteres,
  cortando o excedente); sem edição, o crew carrega o guia do próprio repositório, como antes. O disparo registra só o hash e o tamanho do texto.
- Tabelas: `portal_conhecimento` e `portal_conhecimento_versoes` (RLS ligada, acesso só pelo servidor).
