-- Portal de aprovação: perfis e trilha de auditoria. Aditivo: não altera tabelas existentes.
create table if not exists public.portal_perfis (
  user_id uuid primary key references auth.users(id) on delete cascade,
  nome text not null,
  papel text not null check (papel in ('leitor','revisor','aprovador')),
  criado_em timestamptz not null default now()
);

create table if not exists public.portal_decisoes (
  id bigint generated always as identity primary key,
  execucao_id text not null,          -- execution_id original da cadeia de resumes
  task_id text not null,              -- UUID do human_input
  portao text,                        -- G1 | G2 | G3
  decisao text not null check (decisao in ('aprovar','devolver','reprovar')),
  instrucoes text,
  humano_id uuid not null,
  humano_nome text not null,
  enviado_ao_crewai boolean not null default false,
  novo_kickoff_id text,
  resposta_crewai text,
  criado_em timestamptz not null default now()
);
create index if not exists portal_decisoes_exec on public.portal_decisoes (execucao_id, criado_em desc);

alter table public.portal_perfis enable row level security;
alter table public.portal_decisoes enable row level security;
-- Sem políticas: o acesso é feito só pelo servidor do portal (service role), depois de validar a sessão e o papel.

-- Clientes (carga gerada por scripts/gerar_dados.py a partir de knowledge/INDEX.md) e trilha dos disparos.
create table if not exists public.portal_disparos (
  id bigint generated always as identity primary key,
  humano_id uuid not null,
  humano_nome text not null,
  cliente_slug text not null,
  briefing jsonb not null,
  enviado_ao_crewai boolean not null default false,
  kickoff_id text,
  resposta_crewai text,
  criado_em timestamptz not null default now()
);
create index if not exists portal_disparos_criado on public.portal_disparos (criado_em desc);
alter table public.portal_disparos enable row level security;

-- Tempo real: membros do portal (com perfil) leem as tabelas via Realtime só para saber que algo mudou;
-- as telas então recarregam os dados pelo servidor. Quem não tem perfil não recebe nada.
create or replace function public.portal_membro() returns boolean language sql stable security definer set search_path = '' as $$
  select exists (select 1 from public.portal_perfis where user_id = auth.uid());
$$;
revoke all on function public.portal_membro() from public, anon;
grant execute on function public.portal_membro() to authenticated;
create policy portal_ao_vivo on public.crewai_webhook_events for select to authenticated using (public.portal_membro());
create policy portal_ao_vivo on public.portal_decisoes for select to authenticated using (public.portal_membro());
create policy portal_ao_vivo on public.portal_disparos for select to authenticated using (public.portal_membro());
alter publication supabase_realtime add table public.crewai_webhook_events, public.portal_decisoes, public.portal_disparos;

-- Base de conhecimento editável: edições do guia do repositório e documentos acrescentados, com histórico de versões.
create table if not exists public.portal_conhecimento (
  id bigint generated always as identity primary key,
  cliente_slug text not null references public.portal_clientes(slug) on delete cascade,
  doc_chave text not null, titulo text not null, conteudo text not null,
  origem text not null check (origem in ('base_editada','adicionado')),
  versao int not null default 1, atualizado_por uuid, atualizado_nome text not null, atualizado_em timestamptz not null default now(),
  unique (cliente_slug, doc_chave)
);
create index if not exists portal_conhecimento_cliente on public.portal_conhecimento (cliente_slug);
create table if not exists public.portal_conhecimento_versoes (
  id bigint generated always as identity primary key,
  cliente_slug text not null, doc_chave text not null, titulo text not null, conteudo text not null,
  versao int not null, acao text not null, autor_nome text not null, criado_em timestamptz not null default now()
);
create index if not exists portal_conhecimento_versoes_doc on public.portal_conhecimento_versoes (cliente_slug, doc_chave, criado_em desc);
alter table public.portal_conhecimento enable row level security;
alter table public.portal_conhecimento_versoes enable row level security;
