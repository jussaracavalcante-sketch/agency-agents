-- Endurecimento de segurança e retenção (LGPD). NÃO aplicado: revisar e aplicar no SQL Editor do Supabase com o administrador.
-- Reversível: cada bloco tem o comando inverso no comentário.

-- 1) Privilégios mínimos. O portal acessa o banco só pelo servidor (chave de serviço). As tabelas já negam tudo por RLS sem política,
--    mas os privilégios de tabela continuam concedidos a anon e authenticated. Remover é defesa em profundidade.
revoke all on table
  public.portal_agentes_ajustes, public.portal_auditoria, public.portal_clientes, public.portal_config, public.portal_conhecimento,
  public.portal_conhecimento_versoes, public.portal_convites, public.portal_perfis, public.crewai_config
from anon, authenticated;

-- As três tabelas do tempo real precisam de SELECT para o papel authenticated (política "portal_ao_vivo", só para quem tem perfil). Anon não precisa.
revoke all on table public.portal_decisoes, public.portal_disparos, public.crewai_webhook_events from anon;
revoke insert, update, delete, truncate, references, trigger on table public.portal_decisoes, public.portal_disparos, public.crewai_webhook_events from authenticated;
-- Inverso: grant select, insert, update, delete on table <tabela> to anon, authenticated;

-- 2) A função de papel é usada pela política de tempo real; só usuários logados precisam executá-la.
revoke execute on function public.portal_membro() from public, anon;
grant execute on function public.portal_membro() to authenticated;

-- 3) Auditoria append-only de fato: ninguém altera nem apaga linhas pelo caminho normal (a chave de serviço continua podendo; ver processo de retenção abaixo).
create or replace function public.portal_auditoria_imutavel() returns trigger language plpgsql set search_path = '' as $$
begin
  raise exception 'portal_auditoria é somente de acréscimo';
end $$;
drop trigger if exists portal_auditoria_sem_alteracao on public.portal_auditoria;
create trigger portal_auditoria_sem_alteracao before update or delete on public.portal_auditoria
  for each row execute function public.portal_auditoria_imutavel();
-- Inverso: drop trigger portal_auditoria_sem_alteracao on public.portal_auditoria;

-- 4) Retenção. Os eventos do webhook guardam o texto integral de cada tarefa dos agentes (peças, pareceres, briefing). Prazo proposto: 180 dias.
--    Decisões, disparos e auditoria são registro de responsabilidade e seguem a política da empresa (proposta: 5 anos).
--    A função só apaga quando chamada; agendar (pg_cron ou rotina externa) depois da aprovação do encarregado.
create or replace function public.portal_expurgar_eventos(dias integer default 180) returns integer
language plpgsql security invoker set search_path = '' as $$
declare apagados integer;
begin
  if dias < 30 then raise exception 'Prazo mínimo de 30 dias'; end if;
  delete from public.crewai_webhook_events where recebido_em < now() - make_interval(days => dias);
  get diagnostics apagados = row_count;
  return apagados;
end $$;
revoke execute on function public.portal_expurgar_eventos(integer) from public, anon, authenticated;
-- Uso (administrador, com chave de serviço): select public.portal_expurgar_eventos(180);
