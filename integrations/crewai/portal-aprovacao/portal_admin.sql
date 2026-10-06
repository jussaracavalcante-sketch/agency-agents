-- Administração do portal: papel admin, trilha de auditoria, ajustes dos agentes e configuração (preços e ROI). Aditivo.
alter table public.portal_perfis drop constraint if exists portal_perfis_papel_check;
alter table public.portal_perfis add constraint portal_perfis_papel_check check (papel in ('leitor','revisor','aprovador','admin'));
alter table public.portal_convites drop constraint if exists portal_convites_papel_check;
alter table public.portal_convites add constraint portal_convites_papel_check check (papel in ('leitor','revisor','aprovador','admin'));

-- Trilha de auditoria: quem (nome e sessão), quando, o que mudou (antes/depois). Só o servidor grava; ninguém edita nem apaga pelo portal.
create table if not exists public.portal_auditoria (
  id bigint generated always as identity primary key,
  criado_em timestamptz not null default now(),
  usuario_id uuid,
  usuario_nome text not null,
  sessao text,                       -- id da sessão de login (claim session_id do token)
  acao text not null,                -- decisao.aprovar, disparo.criar, conhecimento.salvar, admin.convite_salvar…
  entidade text not null,            -- portal_decisoes, portal_disparos, portal_conhecimento, portal_perfis…
  entidade_id text,
  antes jsonb,
  depois jsonb,
  detalhe text
);
create index if not exists portal_auditoria_criado on public.portal_auditoria (criado_em desc);
create index if not exists portal_auditoria_usuario on public.portal_auditoria (usuario_nome, criado_em desc);
alter table public.portal_auditoria enable row level security;

-- Ajustes do administrador por agente: texto que vai no contexto de cada campanha (seção [AJUSTES DO ADMINISTRADOR]).
create table if not exists public.portal_agentes_ajustes (
  chave text primary key,            -- chave do agente em agents.yaml (ex.: redator_conteudo)
  ativo boolean not null default true,
  instrucoes text not null default '',
  atualizado_por uuid,
  atualizado_nome text,
  atualizado_em timestamptz not null default now()
);
alter table public.portal_agentes_ajustes enable row level security;

-- Configuração do portal (preços por token, câmbio, valor de referência da campanha para o ROI).
create table if not exists public.portal_config (
  chave text primary key,
  valor text not null,
  descricao text,
  atualizado_em timestamptz not null default now()
);
alter table public.portal_config enable row level security;
insert into public.portal_config (chave, valor, descricao) values
  ('preco_entrada_usd_por_milhao', '3', 'Preço de tokens de entrada (prompt) em US$ por milhão'),
  ('preco_saida_usd_por_milhao', '15', 'Preço de tokens de saída (completion) em US$ por milhão'),
  ('preco_cache_usd_por_milhao', '0.30', 'Preço de tokens de entrada lidos do cache em US$ por milhão'),
  ('cambio_usd_brl', '5.40', 'Câmbio US$ → R$ usado nos cálculos'),
  ('valor_campanha_referencia_brl', '', 'Valor de referência (R$) que uma campanha entregue representa; vazio = ROI não calculado'),
  ('horas_humanas_por_campanha', '', 'Horas de trabalho humano que a campanha substitui (opcional, para o ROI de esforço)'),
  ('custo_hora_humana_brl', '', 'Custo da hora humana em R$ (opcional)')
on conflict (chave) do nothing;

-- A administradora inicial do sistema.
update public.portal_perfis set papel = 'admin'
 where user_id in (select id from auth.users where email ilike 'jussara.cavalcante@vanguardamartech.com.br');
update public.portal_convites set papel = 'admin' where email ilike 'jussara.cavalcante@vanguardamartech.com.br';
