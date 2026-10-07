import { admin, sessaoId, type Usuario } from "./supabase";

export type Registro = {
  id: number; criado_em: string; usuario_id: string | null; usuario_nome: string; sessao: string | null;
  acao: string; entidade: string; entidade_id: string | null; antes: unknown; depois: unknown; detalhe: string | null;
};

/** Grava uma linha na trilha de auditoria. Nunca derruba a operação principal: falha de auditoria vai para o log do servidor. */
export async function registrar(u: Usuario | null, r: { acao: string; entidade: string; entidade_id?: string | number | null; antes?: unknown; depois?: unknown; detalhe?: string }) {
  try {
    const sessao = await sessaoId().catch(() => null);
    await admin().from("portal_auditoria").insert({
      usuario_id: u?.id ?? null, usuario_nome: u?.nome ?? "sistema", sessao,
      acao: r.acao, entidade: r.entidade, entidade_id: r.entidade_id == null ? null : String(r.entidade_id),
      antes: r.antes ?? null, depois: r.depois ?? null, detalhe: r.detalhe ?? null,
    });
  } catch (e) { console.error("[auditoria]", e); }
}

export type Filtro = { usuario?: string; acao?: string; entidade?: string; de?: string; ate?: string; busca?: string; limite?: number };

export async function listar(f: Filtro = {}): Promise<Registro[]> {
  let q = admin().from("portal_auditoria").select("*").order("id", { ascending: false }).limit(Math.min(f.limite ?? 300, 2000));
  if (f.usuario) q = q.ilike("usuario_nome", `%${f.usuario}%`);
  if (f.acao) q = q.ilike("acao", `${f.acao}%`);
  if (f.entidade) q = q.eq("entidade", f.entidade);
  if (f.de) q = q.gte("criado_em", new Date(f.de + "T00:00:00-04:00").toISOString());
  if (f.ate) q = q.lte("criado_em", new Date(f.ate + "T23:59:59-04:00").toISOString());
  if (f.busca) q = q.or(`detalhe.ilike.%${f.busca}%,entidade_id.ilike.%${f.busca}%,sessao.ilike.%${f.busca}%`);
  const { data } = await q;
  return (data || []) as Registro[];
}

/** Resumo legível do que mudou: chaves alteradas entre antes e depois. */
export function mudancas(antes: unknown, depois: unknown): string[] {
  const a = (antes && typeof antes === "object" ? antes : {}) as Record<string, unknown>;
  const d = (depois && typeof depois === "object" ? depois : {}) as Record<string, unknown>;
  const chaves = new Set([...Object.keys(a), ...Object.keys(d)]);
  const out: string[] = [];
  for (const k of chaves) {
    const va = JSON.stringify(a[k]); const vd = JSON.stringify(d[k]);
    if (va === vd) continue;
    const corta = (x: string | undefined) => (x === undefined ? "—" : x.length > 90 ? x.slice(0, 90) + "…" : x);
    out.push(`${k}: ${corta(va)} → ${corta(vd)}`);
  }
  return out;
}

export const ACOES: Record<string, string> = {
  "decisao.aprovar": "Aprovou portão", "decisao.devolver": "Devolveu portão com ajustes", "decisao.reprovar": "Reprovou portão",
  "disparo.criar": "Disparou campanha", "conhecimento.salvar": "Salvou documento de marca", "conhecimento.excluir": "Excluiu documento",
  "conhecimento.restaurar_original": "Restaurou guia original", "conhecimento.restaurar_versao": "Restaurou versão", "conhecimento.completo": "Marcou guia completo/incompleto",
  "admin.convite_salvar": "Salvou convite de acesso", "admin.convite_excluir": "Excluiu convite", "admin.perfil_papel": "Alterou papel/portões", "admin.perfil_excluir": "Removeu acesso",
  "admin.agente_salvar": "Ajustou agente", "admin.config_salvar": "Alterou configuração", "admin.execucao_encerrar": "Encerrou execução", "admin.limpar_testes": "Limpou eventos de teste", "aceite.registrar": "Aceitou documento (privacidade ou conduta)",
};
export const rotuloAcao = (a: string) => ACOES[a] ?? a;
