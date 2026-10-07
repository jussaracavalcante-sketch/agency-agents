import { cache } from "react";
import { admin, sessaoId, type Usuario } from "./supabase";
import { registrar } from "./auditoria";
import { DOCUMENTOS, type Documento } from "./documentos";

export { COOKIE_ACEITE, SELO_VIGENTE } from "./selo";
export const TODOS = Object.values(DOCUMENTOS);

/** Documentos que a pessoa ainda não aceitou na versão em vigor. A fonte da verdade é o banco, nunca o cookie. */
export const pendentesDe = cache(async (userId: string): Promise<Documento[]> => {
  const { data } = await admin().from("portal_aceites").select("documento,hash").eq("user_id", userId);
  const ok = new Set((data || []).map((r) => `${r.documento}:${r.hash}`));
  return TODOS.filter((d) => !ok.has(`${d.chave}:${d.hash}`));
});

export async function registrarAceite(u: Usuario, chaves: string[]) {
  const pend = await pendentesDe(u.id);
  const alvo = pend.filter((d) => chaves.includes(d.chave));
  if (!alvo.length) return [];
  const sessao = await sessaoId().catch(() => null);
  const { error } = await admin().from("portal_aceites").insert(alvo.map((d) => ({ user_id: u.id, usuario_nome: u.nome, documento: d.chave, versao: d.versao, hash: d.hash, sessao })));
  if (error) throw new Error(error.message);
  for (const d of alvo) {
    await registrar(u, { acao: "aceite.registrar", entidade: "portal_aceites", entidade_id: d.chave, depois: { documento: d.titulo, versao: d.versao, hash: d.hash }, detalhe: `Aceitou ${d.titulo} (versão ${d.versao}).` });
  }
  return alvo;
}
