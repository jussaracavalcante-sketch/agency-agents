import Link from "next/link";
import { redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";
import { fmt } from "@/lib/dados";

export const dynamic = "force-dynamic";

export default async function Conhecimento({ searchParams: sp }: { searchParams: Promise<{ f?: string; q?: string }> }) {
  const searchParams = await sp;
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const [{ data }, { data: edits }] = await Promise.all([
    admin().from("portal_clientes").select("slug,nome,guia_completo,guia_caracteres,atualizado_em").order("nome"),
    admin().from("portal_conhecimento").select("cliente_slug,origem,atualizado_em"),
  ]);
  const todos = data || [];
  const porCliente = new Map<string, { editado: boolean; extras: number; ultimo: string }>();
  for (const e of edits || []) {
    const c = porCliente.get(e.cliente_slug) || { editado: false, extras: 0, ultimo: "" };
    if (e.origem === "base_editada") c.editado = true; else c.extras++;
    if (e.atualizado_em > c.ultimo) c.ultimo = e.atualizado_em;
    porCliente.set(e.cliente_slug, c);
  }
  const q = (searchParams.q || "").trim().toLowerCase();
  const inc = searchParams.f === "incompletos";
  const alt = searchParams.f === "alterados";
  const lista = todos.filter((c) => (!inc || !c.guia_completo) && (!alt || porCliente.has(c.slug)) && (!q || c.nome.toLowerCase().includes(q)));
  const podeEditar = u.papel !== "leitor";
  return (
    <>
      <div className="head"><div><h1>Conhecimento</h1><p className="sub" style={{ margin: 0 }}>Guias de marca que os agentes leem antes de cada campanha. {podeEditar ? "Abra um cliente para editar o guia ou acrescentar documentos." : "Seu papel permite só consultar."}</p></div></div>
      <form className="busca" action="/conhecimento"><input name="q" defaultValue={searchParams.q || ""} placeholder="Buscar cliente…" />{searchParams.f && <input type="hidden" name="f" value={searchParams.f} />}</form>
      <div className="chips">
        <Link href="/conhecimento" className={!inc && !alt ? "on" : ""}>Todos {todos.length}</Link>
        <Link href="/conhecimento?f=incompletos" className={inc ? "on" : ""}>Incompletos {todos.filter((c) => !c.guia_completo).length}</Link>
        <Link href="/conhecimento?f=alterados" className={alt ? "on" : ""}>Alterados no portal {porCliente.size}</Link>
      </div>
      <div className="card">
        <table className="tb"><thead><tr><th>Cliente</th><th>Guia</th><th>Portal</th><th>Tamanho</th><th></th></tr></thead><tbody>
          {lista.map((c) => {
            const p = porCliente.get(c.slug);
            return (
              <tr key={c.slug}>
                <td><Link href={`/conhecimento/${c.slug}`}>{c.nome}</Link></td>
                <td>{c.guia_completo ? <span className="st ok">Completo</span> : <span className="st warn">Incompleto</span>}</td>
                <td className="mut">{p ? <>{p.editado ? "guia editado" : "guia original"}{p.extras ? ` · +${p.extras} doc(s)` : ""}<br />{fmt(p.ultimo)}</> : "original do repositório"}</td>
                <td className="mut">{c.guia_caracteres.toLocaleString("pt-BR")} caracteres</td>
                <td><Link className="btn" href={`/conhecimento/${c.slug}`}>{podeEditar ? "Editar" : "Ver"}</Link></td>
              </tr>
            );
          })}
        </tbody></table>
        {!lista.length && <p className="vazio">Nenhum cliente encontrado.</p>}
      </div>
    </>
  );
}
