import Link from "next/link";
import { notFound, redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { docsEfetivos, LIMITE_CONTEXTO, LIMITE_DOC } from "@/lib/conhecimento";
import Editor from "./Editor";

export const dynamic = "force-dynamic";

export default async function Cliente({ params }: { params: { slug: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const db = admin();
  const { data: cliente } = await db.from("portal_clientes").select("slug,nome,guia_completo").eq("slug", params.slug).maybeSingle();
  if (!cliente) notFound();
  const [{ docs, repoOk }, { data: versoes }] = await Promise.all([
    docsEfetivos(cliente.slug),
    db.from("portal_conhecimento_versoes").select("id,doc_chave,versao,acao,autor_nome,criado_em").eq("cliente_slug", cliente.slug).order("criado_em", { ascending: false }).limit(60),
  ]);
  return (
    <>
      <div className="head">
        <div>
          <div className="mut"><Link href="/conhecimento">Conhecimento</Link> › {cliente.nome}</div>
          <h1>{cliente.nome}</h1>
          <p className="sub" style={{ margin: 0 }}>O que você salvar aqui é o que os agentes leem na próxima campanha deste cliente.</p>
        </div>
      </div>
      <Editor slug={cliente.slug} nome={cliente.nome} completo={cliente.guia_completo} docs={docs} versoes={versoes || []} repoOk={repoOk}
        podeEditar={u.papel !== "leitor"} limiteContexto={LIMITE_CONTEXTO} limiteDoc={LIMITE_DOC} />
    </>
  );
}
