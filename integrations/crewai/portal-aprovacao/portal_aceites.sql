-- Aceite do aviso de privacidade e do termo de conduta (registro por pessoa, documento, versão e hash do texto).
-- JÁ APLICADO no Supabase em 07/10/2026. Mantido aqui como registro.
create table if not exists public.portal_aceites (
  id bigserial primary key,
  user_id uuid not null,
  usuario_nome text not null,
  documento text not null check (documento in ('aviso','termo')),
  versao text not null,
  hash text not null,
  sessao text,
  aceito_em timestamptz not null default now(),
  unique (user_id, documento, hash)
);
alter table public.portal_aceites enable row level security;
revoke all on table public.portal_aceites from anon, authenticated;
revoke all on sequence public.portal_aceites_id_seq from anon, authenticated;
-- Registro imutável: reaproveita a função do gatilho da auditoria.
create trigger portal_aceites_sem_alteracao before update or delete on public.portal_aceites for each row execute function public.portal_auditoria_imutavel();
