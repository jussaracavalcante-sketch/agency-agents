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
