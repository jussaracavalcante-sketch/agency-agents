import { createHash } from "crypto";
import { admin } from "./supabase";

/** Base do repositório (público): um guia por cliente em knowledge/<slug>/guia_identidade_visual.md. */
const RAW = process.env.KNOWLEDGE_RAW_BASE || "https://raw.githubusercontent.com/jussaracavalcante-sketch/agency-agents/main/integrations/crewai/marketing-operations/knowledge";
export const BASE_CHAVE = "guia_identidade_visual.md";
export const BASE_TITULO = "Guia de identidade visual";
/** Tamanho máximo do texto de marca enviado aos agentes (cada tarefa o recebe no prompt). */
export const LIMITE_CONTEXTO = 10_000;
export const LIMITE_DOC = 60_000;
/** Documento sincronizado do setup de IA do cliente no VJOB (Nekt). Somente leitura no portal. */
export const VJOB_CHAVE = "setup_vjob.md";
export const VJOB_TITULO = "Setup de IA no VJOB (Nekt)";
export const MAX_ADICIONADOS = 20;

export type Doc = {
  chave: string; titulo: string; conteudo: string;
  origem: "repo" | "base_editada" | "adicionado" | "vjob";
  versao?: number; atualizado_nome?: string; atualizado_em?: string;
  /** início e fim do documento no texto final; usados para avisar o que passa do limite */
  corte?: "dentro" | "parcial" | "fora";
};

export async function textoDoRepo(slug: string): Promise<string | null> {
  try {
    const r = await fetch(`${RAW}/${encodeURIComponent(slug)}/${BASE_CHAVE}`, { next: { revalidate: 120 } });
    return r.ok ? await r.text() : null;
  } catch { return null; }
}

type Linha = { doc_chave: string; titulo: string; conteudo: string; origem: "base_editada" | "adicionado"; versao: number; atualizado_nome: string; atualizado_em: string };

export async function linhasDoCliente(slug: string): Promise<Linha[]> {
  const { data } = await admin().from("portal_conhecimento").select("doc_chave,titulo,conteudo,origem,versao,atualizado_nome,atualizado_em").eq("cliente_slug", slug).order("titulo");
  return (data || []) as Linha[];
}

export type SetupVjob = { conteudo: string; chars: number; nome_vjob: string; id_cliente_vjob: number; sincronizado_em: string; vjob_atualizado_em: string | null };

/** Setup de IA do cliente no VJOB, sincronizado da Nekt (portal_vjob_setup). Só entra quando o setup tem conteúdo. */
export async function setupVjob(slug: string): Promise<SetupVjob | null> {
  const { data } = await admin().from("portal_vjob_setup").select("conteudo,chars,nome_vjob,id_cliente_vjob,sincronizado_em,vjob_atualizado_em").eq("cliente_slug", slug).eq("status", "ok").maybeSingle();
  return data && String(data.conteudo || "").trim() ? (data as SetupVjob) : null;
}

/** Teto do texto de marca: o padrão mais o documento do VJOB inteiro, para ele nunca cortar o guia nem ser cortado. */
export const limiteDoCliente = (vjob: SetupVjob | null) => LIMITE_CONTEXTO + (vjob ? vjob.chars + 2 : 0);

/** Documentos que os agentes recebem: guia do repositório (ou a versão editada) mais os documentos acrescentados. */
export async function docsEfetivos(slug: string): Promise<{ docs: Doc[]; repoOk: boolean; repoTexto: string | null }> {
  const [linhas, repoTexto, vjob] = await Promise.all([linhasDoCliente(slug), textoDoRepo(slug), setupVjob(slug)]);
  const docs: Doc[] = [];
  const edit = linhas.find((l) => l.doc_chave === BASE_CHAVE);
  if (edit) docs.push({ chave: BASE_CHAVE, titulo: edit.titulo, conteudo: edit.conteudo, origem: "base_editada", versao: edit.versao, atualizado_nome: edit.atualizado_nome, atualizado_em: edit.atualizado_em });
  else if (repoTexto !== null) docs.push({ chave: BASE_CHAVE, titulo: BASE_TITULO, conteudo: repoTexto, origem: "repo" });
  if (vjob) docs.push({ chave: VJOB_CHAVE, titulo: VJOB_TITULO, conteudo: vjob.conteudo, origem: "vjob", atualizado_nome: `VJOB (${vjob.nome_vjob})`, atualizado_em: vjob.sincronizado_em });
  for (const l of linhas.filter((x) => x.doc_chave !== BASE_CHAVE && x.doc_chave !== VJOB_CHAVE)) {
    docs.push({ chave: l.doc_chave, titulo: l.titulo, conteudo: l.conteudo, origem: "adicionado", versao: l.versao, atualizado_nome: l.atualizado_nome, atualizado_em: l.atualizado_em });
  }
  let usado = 0;
  for (const d of docs) {
    const tam = montarBloco(d).length + 2;
    const teto = limiteDoCliente(vjob);
    d.corte = usado + tam <= teto ? "dentro" : usado < teto ? "parcial" : "fora";
    usado += tam;
  }
  return { docs, repoOk: repoTexto !== null || !!edit, repoTexto };
}

const montarBloco = (d: Pick<Doc, "chave" | "conteudo">) => `=== ${d.chave} ===\n${d.conteudo.trim()}`;

/**
 * Texto de marca para o disparo. Sem edições nem documentos acrescentados devolve null: o crew carrega o guia do próprio
 * repositório (caminho já validado). Com edições, monta o texto efetivo; se o guia do repositório não puder ser lido
 * e não foi editado, devolve erro em vez de enviar uma base sem o guia.
 */
export async function contextoDoCliente(slug: string): Promise<{ texto: string | null; hash?: string; docs?: number; chars?: number; truncado?: boolean; erro?: string }> {
  const [linhas, vjob] = await Promise.all([linhasDoCliente(slug), setupVjob(slug)]);
  if (!linhas.length && !vjob) return { texto: null };
  const { docs, repoOk } = await docsEfetivos(slug);
  if (!repoOk) return { texto: null, erro: "Não foi possível carregar o guia do repositório para montar a base do cliente. Tente novamente em instantes." };
  const completo = docs.map(montarBloco).join("\n\n");
  const teto = limiteDoCliente(vjob);
  const texto = completo.slice(0, teto);
  return { texto, hash: createHash("sha256").update(texto).digest("hex").slice(0, 12), docs: docs.length, chars: texto.length, truncado: completo.length > teto };
}

/** Atualiza o tamanho do guia em portal_clientes (soma dos documentos efetivos). */
export async function atualizarMetadadosDoCliente(slug: string) {
  const { docs, repoOk } = await docsEfetivos(slug);
  if (!repoOk) return;
  const total = docs.reduce((n, d) => n + d.conteudo.length, 0);
  await admin().from("portal_clientes").update({ guia_caracteres: total, atualizado_em: new Date().toISOString() }).eq("slug", slug);
}

export const slugDoTitulo = (t: string) =>
  t.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "_").replace(/^_+|_+$/g, "").slice(0, 60) || "documento";
