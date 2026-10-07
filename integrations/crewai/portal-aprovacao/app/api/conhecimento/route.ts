import { NextResponse } from "next/server";
import { admin, usuarioAtual } from "@/lib/supabase";
import { registrar } from "@/lib/auditoria";
import { dadosPessoais, mensagemDadosPessoais } from "@/lib/dadosPessoais";
import { BASE_CHAVE, BASE_TITULO, VJOB_CHAVE, LIMITE_DOC, MAX_ADICIONADOS, atualizarMetadadosDoCliente, slugDoTitulo, textoDoRepo } from "@/lib/conhecimento";

export const dynamic = "force-dynamic";

type Corpo = { acao?: string; slug?: string; chave?: string; titulo?: string; conteudo?: string; versao?: number; versaoId?: number; completo?: boolean };
const erro = (mensagem: string, status = 400) => NextResponse.json({ erro: mensagem }, { status });

export async function POST(req: Request) {
  const u = await usuarioAtual();
  if (!u) return erro("Sessão inválida", 401);
  if (u.papel === "leitor") return erro("Seu papel não permite editar a base de conhecimento", 403);
  const b = ((await req.json().catch(() => null)) || {}) as Corpo;
  const db = admin();
  const slug = String(b.slug || "");
  const { data: cliente } = await db.from("portal_clientes").select("slug,nome").eq("slug", slug).maybeSingle();
  if (!cliente) return erro("Cliente não encontrado");

  const snapshot = (d: { doc_chave: string; titulo: string; conteudo: string; versao: number }, acao: string) =>
    db.from("portal_conhecimento_versoes").insert({ cliente_slug: slug, doc_chave: d.doc_chave, titulo: d.titulo, conteudo: d.conteudo, versao: d.versao, acao, autor_nome: u.nome });

  async function gravar(chave: string, titulo: string, conteudo: string, versaoEsperada: number | undefined, acao: string) {
    const origem = chave === BASE_CHAVE ? "base_editada" : "adicionado";
    const { data: atual } = await db.from("portal_conhecimento").select("*").eq("cliente_slug", slug).eq("doc_chave", chave).maybeSingle();
    if (atual) {
      if (versaoEsperada !== undefined && versaoEsperada !== atual.versao) return erro(`${atual.atualizado_nome} salvou uma versão mais nova deste documento. Recarregue a página antes de editar.`, 409);
      await snapshot(atual, acao);
      const { error } = await db.from("portal_conhecimento").update({ titulo, conteudo, versao: atual.versao + 1, atualizado_por: u!.id, atualizado_nome: u!.nome, atualizado_em: new Date().toISOString() }).eq("id", atual.id);
      if (error) return erro("Não foi possível salvar", 500);
    } else {
      if (origem === "adicionado") {
        const { count } = await db.from("portal_conhecimento").select("id", { count: "exact", head: true }).eq("cliente_slug", slug).eq("origem", "adicionado");
        if ((count ?? 0) >= MAX_ADICIONADOS) return erro(`Limite de ${MAX_ADICIONADOS} documentos acrescentados por cliente`);
      } else {
        const original = await textoDoRepo(slug); // guarda o texto original como versão 0, para poder voltar a ele
        if (original !== null) await snapshot({ doc_chave: chave, titulo: BASE_TITULO, conteudo: original, versao: 0 }, "original");
      }
      const { error } = await db.from("portal_conhecimento").insert({ cliente_slug: slug, doc_chave: chave, titulo, conteudo, origem, versao: 1, atualizado_por: u!.id, atualizado_nome: u!.nome });
      if (error) return erro("Não foi possível salvar", 500);
    }
    await atualizarMetadadosDoCliente(slug);
    await registrar(u, { acao: acao === "novo" ? "conhecimento.salvar" : `conhecimento.${acao}`, entidade: "portal_conhecimento", entidade_id: `${slug}/${chave}`, antes: atual ? { titulo: atual.titulo, versao: atual.versao, chars: String(atual.conteudo).length } : null, depois: { titulo, versao: atual ? atual.versao + 1 : 1, chars: conteudo.length }, detalhe: `${cliente!.nome}: documento ${chave} (${acao}).` });
    return NextResponse.json({ ok: true, mensagem: "Salvo. A próxima campanha disparada já usa esta versão." });
  }

  switch (b.acao) {
    case "salvar": {
      const titulo = String(b.titulo || "").trim();
      const conteudo = String(b.conteudo || "");
      if (!titulo || titulo.length > 120) return erro("Informe um título de até 120 caracteres");
      if (!conteudo.trim()) return erro("O conteúdo não pode ficar vazio");
      const achados = dadosPessoais(`${titulo}\n${conteudo}`, { contatos: false });
      if (achados.length) return erro(mensagemDadosPessoais(achados));
      if (conteudo.length > LIMITE_DOC) return erro(`O documento passa de ${LIMITE_DOC.toLocaleString("pt-BR")} caracteres`);
      let chave = String(b.chave || "");
      if (!chave) { // documento novo
        const base = slugDoTitulo(titulo);
        const { data: existentes } = await db.from("portal_conhecimento").select("doc_chave").eq("cliente_slug", slug);
        const usadas = new Set((existentes || []).map((x) => x.doc_chave as string));
        chave = `${base}.md`;
        for (let i = 2; usadas.has(chave) || chave === BASE_CHAVE || chave === VJOB_CHAVE; i++) chave = `${base}_${i}.md`;
        return gravar(chave, titulo, conteudo, undefined, "novo");
      }
      if (chave === VJOB_CHAVE) return erro("O setup do VJOB é sincronizado da Nekt e não se edita aqui. Altere no VJOB.");
      if (chave !== BASE_CHAVE && !/^[a-z0-9_]+\.md$/.test(chave)) return erro("Documento inválido");
      return gravar(chave, chave === BASE_CHAVE ? BASE_TITULO : titulo, conteudo, b.versao, "salvar");
    }
    case "restaurar_original": {
      const { data: atual } = await db.from("portal_conhecimento").select("*").eq("cliente_slug", slug).eq("doc_chave", BASE_CHAVE).maybeSingle();
      if (!atual) return erro("O guia já está na versão original");
      await snapshot(atual, "restaurar_original");
      await db.from("portal_conhecimento").delete().eq("id", atual.id);
      await atualizarMetadadosDoCliente(slug);
      await registrar(u, { acao: "conhecimento.restaurar_original", entidade: "portal_conhecimento", entidade_id: `${slug}/${BASE_CHAVE}`, antes: { versao: atual.versao, chars: String(atual.conteudo).length }, detalhe: `${cliente.nome}: guia restaurado ao original.` });
      return NextResponse.json({ ok: true, mensagem: "Guia restaurado para a versão do repositório." });
    }
    case "excluir": {
      const chave = String(b.chave || "");
      if (chave === BASE_CHAVE) return erro("O guia base não pode ser excluído; use “Restaurar original”");
      const { data: atual } = await db.from("portal_conhecimento").select("*").eq("cliente_slug", slug).eq("doc_chave", chave).maybeSingle();
      if (!atual) return erro("Documento não encontrado", 404);
      await snapshot(atual, "excluir");
      await db.from("portal_conhecimento").delete().eq("id", atual.id);
      await atualizarMetadadosDoCliente(slug);
      await registrar(u, { acao: "conhecimento.excluir", entidade: "portal_conhecimento", entidade_id: `${slug}/${chave}`, antes: { titulo: atual.titulo, versao: atual.versao, chars: String(atual.conteudo).length }, detalhe: `${cliente.nome}: documento excluído.` });
      return NextResponse.json({ ok: true, mensagem: "Documento excluído (a versão fica no histórico)." });
    }
    case "restaurar_versao": {
      const { data: v } = await db.from("portal_conhecimento_versoes").select("*").eq("id", Number(b.versaoId)).eq("cliente_slug", slug).maybeSingle();
      if (!v) return erro("Versão não encontrada", 404);
      return gravar(v.doc_chave, v.titulo, v.conteudo, undefined, "restaurar_versao");
    }
    case "completo": {
      await db.from("portal_clientes").update({ guia_completo: !!b.completo, atualizado_em: new Date().toISOString() }).eq("slug", slug);
      await registrar(u, { acao: "conhecimento.completo", entidade: "portal_clientes", entidade_id: slug, depois: { guia_completo: !!b.completo }, detalhe: `${cliente.nome}: guia marcado como ${b.completo ? "completo" : "incompleto"}.` });
      return NextResponse.json({ ok: true, mensagem: b.completo ? "Guia marcado como completo." : "Guia marcado como incompleto." });
    }
    default:
      return erro("Ação inválida");
  }
}
