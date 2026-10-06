import { admin } from "./supabase";
import { AGENTES } from "./agentes";

export type Ajuste = { chave: string; ativo: boolean; instrucoes: string; atualizado_nome: string | null; atualizado_em: string | null };
export const LIMITE_AJUSTE = 1200;
export const MARCA_AJUSTES = "[AJUSTES DO ADMINISTRADOR]";

export async function ajustesDosAgentes(): Promise<Ajuste[]> {
  const { data } = await admin().from("portal_agentes_ajustes").select("chave,ativo,instrucoes,atualizado_nome,atualizado_em");
  const m = new Map((data || []).map((x) => [x.chave as string, x as Ajuste]));
  return AGENTES.map((a) => m.get(a.chave) ?? { chave: a.chave, ativo: true, instrucoes: "", atualizado_nome: null, atualizado_em: null });
}

/** Bloco que vai no contexto da campanha: uma seção por agente com ajuste ativo. Vazio se não houver ajuste. */
export async function textoDosAjustes(): Promise<string> {
  const ajustes = (await ajustesDosAgentes()).filter((a) => a.ativo && a.instrucoes.trim());
  if (!ajustes.length) return "";
  const papel = new Map(AGENTES.map((a) => [a.chave, a.papel]));
  const blocos = ajustes.map((a) => `### ${papel.get(a.chave) ?? a.chave}\n${a.instrucoes.trim().slice(0, LIMITE_AJUSTE)}`);
  return `${MARCA_AJUSTES}\nInstruções do administrador do sistema, por agente. Cada agente segue só a seção do seu papel; elas complementam a tarefa e não liberam dado sem fonte nem removem marcações [VALIDAR].\n\n${blocos.join("\n\n")}\n`;
}

export type Config = Record<string, string>;
export const CHAVES_CONFIG = ["preco_entrada_usd_por_milhao", "preco_saida_usd_por_milhao", "preco_cache_usd_por_milhao", "cambio_usd_brl", "valor_campanha_referencia_brl", "horas_humanas_por_campanha", "custo_hora_humana_brl"] as const;

export async function lerConfig(): Promise<{ valores: Config; descricoes: Config }> {
  const { data } = await admin().from("portal_config").select("chave,valor,descricao");
  const valores: Config = {}; const descricoes: Config = {};
  for (const x of data || []) { valores[x.chave as string] = x.valor as string; descricoes[x.chave as string] = (x.descricao as string) || ""; }
  return { valores, descricoes };
}

export const num = (v: string | undefined, padrao = 0) => { const n = parseFloat(String(v ?? "").replace(",", ".")); return Number.isFinite(n) ? n : padrao; };

/** Estado da plataforma que o portal só observa (as chaves ficam nas variáveis de ambiente da plataforma e da Vercel). */
export function estadoDaPlataforma() {
  return [
    { item: "Publicação automática", valor: "desligada (CREW_ENABLE_WRITE_TOOLS=false)", nota: "Nada é publicado pela crew; o G3 só autoriza." },
    { item: "Portões humanos", valor: "ligados (CREW_HUMAN_GATES=true)", nota: "G1, G2 e G3 pausam a execução até a decisão no portal." },
    { item: "Memória entre execuções", valor: "desligada (CREW_MEMORY=false)", nota: "Evita que fatos inventados voltem como memória." },
    { item: "Integração CrewAI", valor: process.env.CREWAI_API_URL ? "configurada" : "ausente", nota: "CREWAI_API_URL e CREWAI_TOKEN só no servidor." },
    { item: "Webhooks", valor: process.env.WEBHOOK_BASE ? "configurados" : "ausentes", nota: "Eventos task, crew e human_input." },
  ];
}
