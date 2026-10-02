# Portal de aprovação (Next.js na Vercel)

Interface para a equipe validar os portões G1, G2 e G3 do fluxo de marketing no CrewAI. Lê os eventos que o receptor
(Edge Function `crewai-webhook`) grava no Supabase e envia a decisão ao `/resume` da plataforma.

## O que faz
| Tela | Função |
|---|---|
| `/` | Fila de portões pendentes e execuções recentes. |
| `/execucao/[id]` | Pedido do portão, entregas geradas (uma a uma) e histórico de decisões. |
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
