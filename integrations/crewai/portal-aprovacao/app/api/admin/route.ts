import { NextResponse } from "next/server";
import { admin, ehAdmin, usuarioAtual } from "@/lib/supabase";
import { registrar } from "@/lib/auditoria";
import { CHAVES_CONFIG, LIMITE_AJUSTE } from "@/lib/admin";
import { AGENTES } from "@/lib/agentes";
import { obterExecucao } from "@/lib/execucoes";

export const dynamic = "force-dynamic";
const erro = (m: string, status = 400) => NextResponse.json({ erro: m }, { status });
const PAPEIS = ["leitor", "revisor", "aprovador", "admin"];
const PORTOES = ["G1", "G2", "G3"];

type Corpo = { acao?: string; email?: string; nome?: string; cargo?: string; papel?: string; portoes?: string[] | null; userId?: string; chave?: string; ativo?: boolean; instrucoes?: string; valores?: Record<string, string>; execucaoId?: string; motivo?: string };

export async function POST(req: Request) {
  const u = await usuarioAtual();
  if (!u) return erro("Sessão inválida", 401);
  if (!ehAdmin(u)) return erro("Apenas o administrador do sistema acessa esta função", 403);
  const b = (await req.json()) as Corpo;
  const db = admin();
  const portoes = (p: string[] | null | undefined) => (Array.isArray(p) && p.length ? p.filter((x) => PORTOES.includes(x)) : null);

  switch (b.acao) {
    case "convite_salvar": {
      const email = String(b.email || "").trim().toLowerCase();
      if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return erro("E-mail inválido");
      const nome = String(b.nome || "").trim(); if (!nome) return erro("Informe o nome");
      if (!PAPEIS.includes(String(b.papel))) return erro("Papel inválido");
      const { data: antes } = await db.from("portal_convites").select("*").ilike("email", email).maybeSingle();
      const depois = { email, nome, cargo: String(b.cargo || "").trim() || null, papel: b.papel, portoes: portoes(b.portoes) };
      const { error } = await db.from("portal_convites").upsert(depois, { onConflict: "email" });
      if (error) return erro("Não foi possível salvar o convite", 500);
      await registrar(u, { acao: "admin.convite_salvar", entidade: "portal_convites", entidade_id: email, antes, depois });
      return NextResponse.json({ ok: true, mensagem: antes ? "Convite atualizado." : "Convite criado. A pessoa entra com o e-mail informado." });
    }
    case "convite_excluir": {
      const email = String(b.email || "").trim().toLowerCase();
      const { data: antes } = await db.from("portal_convites").select("*").ilike("email", email).maybeSingle();
      if (!antes) return erro("Convite não encontrado", 404);
      await db.from("portal_convites").delete().ilike("email", email);
      await registrar(u, { acao: "admin.convite_excluir", entidade: "portal_convites", entidade_id: email, antes });
      return NextResponse.json({ ok: true, mensagem: "Convite excluído. Quem já tem perfil continua até o perfil ser removido." });
    }
    case "perfil_papel": {
      const userId = String(b.userId || "");
      if (!PAPEIS.includes(String(b.papel))) return erro("Papel inválido");
      const { data: antes } = await db.from("portal_perfis").select("*").eq("user_id", userId).maybeSingle();
      if (!antes) return erro("Perfil não encontrado", 404);
      if (antes.user_id === u.id && b.papel !== "admin") return erro("Você não pode remover o próprio papel de administrador");
      const depois = { papel: b.papel, portoes: portoes(b.portoes) };
      const { error } = await db.from("portal_perfis").update(depois).eq("user_id", userId);
      if (error) return erro("Não foi possível alterar o perfil", 500);
      await registrar(u, { acao: "admin.perfil_papel", entidade: "portal_perfis", entidade_id: userId, antes: { papel: antes.papel, portoes: antes.portoes, nome: antes.nome }, depois: { ...depois, nome: antes.nome } });
      return NextResponse.json({ ok: true, mensagem: "Perfil atualizado. Vale no próximo carregamento de página da pessoa." });
    }
    case "perfil_excluir": {
      const userId = String(b.userId || "");
      if (userId === u.id) return erro("Você não pode remover o próprio acesso");
      const { data: antes } = await db.from("portal_perfis").select("*").eq("user_id", userId).maybeSingle();
      if (!antes) return erro("Perfil não encontrado", 404);
      await db.from("portal_perfis").delete().eq("user_id", userId);
      await registrar(u, { acao: "admin.perfil_excluir", entidade: "portal_perfis", entidade_id: userId, antes });
      return NextResponse.json({ ok: true, mensagem: "Acesso removido. Se o convite continuar ativo, a pessoa volta a receber perfil no próximo login: exclua o convite também, se for o caso." });
    }
    case "agente_salvar": {
      const chave = String(b.chave || "");
      if (!AGENTES.some((a) => a.chave === chave)) return erro("Agente desconhecido");
      const instrucoes = String(b.instrucoes || "");
      if (instrucoes.length > LIMITE_AJUSTE) return erro(`As instruções passam de ${LIMITE_AJUSTE} caracteres`);
      const { data: antes } = await db.from("portal_agentes_ajustes").select("*").eq("chave", chave).maybeSingle();
      const depois = { chave, ativo: b.ativo !== false, instrucoes, atualizado_por: u.id, atualizado_nome: u.nome, atualizado_em: new Date().toISOString() };
      const { error } = await db.from("portal_agentes_ajustes").upsert(depois, { onConflict: "chave" });
      if (error) return erro("Não foi possível salvar o ajuste", 500);
      await registrar(u, { acao: "admin.agente_salvar", entidade: "portal_agentes_ajustes", entidade_id: chave, antes: antes ? { ativo: antes.ativo, instrucoes: antes.instrucoes } : null, depois: { ativo: depois.ativo, instrucoes } });
      return NextResponse.json({ ok: true, mensagem: "Ajuste salvo. A próxima campanha disparada já leva estas instruções no contexto do agente." });
    }
    case "config_salvar": {
      const valores = b.valores || {};
      const { data: atuais } = await db.from("portal_config").select("chave,valor");
      const antes: Record<string, string> = {}; for (const x of atuais || []) antes[x.chave as string] = x.valor as string;
      const depois: Record<string, string> = {};
      for (const k of CHAVES_CONFIG) {
        if (!(k in valores)) continue;
        const v = String(valores[k] ?? "").trim().replace(",", ".");
        if (v && !/^\d+(\.\d+)?$/.test(v)) return erro(`Valor inválido em ${k}: use número com ponto decimal`);
        depois[k] = v;
        await db.from("portal_config").update({ valor: v, atualizado_em: new Date().toISOString() }).eq("chave", k);
      }
      await registrar(u, { acao: "admin.config_salvar", entidade: "portal_config", antes: Object.fromEntries(Object.keys(depois).map((k) => [k, antes[k]])), depois });
      return NextResponse.json({ ok: true, mensagem: "Configuração salva. A análise de ROI já usa os novos valores." });
    }
    case "execucao_encerrar": {
      const id = String(b.execucaoId || "");
      const exec = await obterExecucao(id);
      if (!exec) return erro("Execução não encontrada", 404);
      if (exec.concluida) return erro("Esta execução já está concluída ou encerrada");
      if (!exec.pendente) return erro("Só é possível encerrar execução parada em um portão (em andamento, aguarde o portão)");
      const motivo = String(b.motivo || "Encerrada pelo administrador do sistema").trim();
      await db.from("portal_decisoes").insert({ execucao_id: id, task_id: exec.pendente.task_name, portao: exec.portao, decisao: "reprovar", instrucoes: motivo, humano_id: u.id, humano_nome: u.nome, enviado_ao_crewai: false });
      await registrar(u, { acao: "admin.execucao_encerrar", entidade: "portal_decisoes", entidade_id: id, depois: { portao: exec.portao, motivo }, detalhe: `Execução ${id.slice(0, 8)} encerrada no portal (plataforma segue pausada; nada é publicado).` });
      return NextResponse.json({ ok: true, mensagem: "Execução encerrada no portal." });
    }
    case "limpar_testes": {
      const { count } = await db.from("crewai_webhook_events").select("id", { count: "exact", head: true }).like("kickoff_id", "teste-%");
      await db.from("crewai_webhook_events").delete().like("kickoff_id", "teste-%");
      await registrar(u, { acao: "admin.limpar_testes", entidade: "crewai_webhook_events", detalhe: `${count ?? 0} evento(s) de teste removido(s)` });
      return NextResponse.json({ ok: true, mensagem: `${count ?? 0} evento(s) de teste removido(s).` });
    }
    default:
      return erro("Ação inválida");
  }
}
