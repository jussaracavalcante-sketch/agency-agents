import { admin } from "./supabase";

import { LIMITE_DISPAROS_PADRAO } from "./tamanhos";
export { MAX_FEEDBACK, MAX_CAMPO, MAX_CAMPO_LONGO, LIMITE_DISPAROS_PADRAO } from "./tamanhos";

/** Limite diário de disparos por pessoa (janela de 24 horas). Configurável em Administração, chave limite_disparos_dia. */
export async function limiteDiario(): Promise<number> {
  const { data } = await admin().from("portal_config").select("valor").eq("chave", "limite_disparos_dia").maybeSingle();
  const n = parseInt(String(data?.valor ?? ""), 10);
  return Number.isFinite(n) && n > 0 ? n : LIMITE_DISPAROS_PADRAO;
}

export async function disparosNas24h(userId: string): Promise<number> {
  const desde = new Date(Date.now() - 24 * 3600 * 1000).toISOString();
  const { count } = await admin().from("portal_disparos").select("id", { count: "exact", head: true }).eq("humano_id", userId).gt("criado_em", desde);
  return count ?? 0;
}
