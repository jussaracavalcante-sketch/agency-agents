import Link from "next/link";
import { redirect } from "next/navigation";
import { admin, usuarioAtual } from "@/lib/supabase";

export const dynamic = "force-dynamic";

export default async function Conhecimento({ searchParams }: { searchParams: { f?: string; q?: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const { data } = await admin().from("portal_clientes").select("slug,nome,guia_completo,guia_caracteres,atualizado_em").order("nome");
  const todos = data || [];
  const q = (searchParams.q || "").trim().toLowerCase();
  const inc = searchParams.f === "incompletos";
  const lista = todos.filter((c) => (!inc || !c.guia_completo) && (!q || c.nome.toLowerCase().includes(q)));
  return (
    <>
      <div className="head"><div><h1>Conhecimento</h1><p className="sub" style={{ margin: 0 }}>Guias de marca carregados pelos agentes antes de cada campanha.</p></div></div>
      <form className="busca" action="/conhecimento"><input name="q" defaultValue={searchParams.q || ""} placeholder="Buscar cliente…" />{inc && <input type="hidden" name="f" value="incompletos" />}</form>
      <div className="chips">
        <Link href="/conhecimento" className={!inc ? "on" : ""}>Todos {todos.length}</Link>
        <Link href="/conhecimento?f=incompletos" className={inc ? "on" : ""}>Incompletos {todos.filter((c) => !c.guia_completo).length}</Link>
      </div>
      <div className="card">
        <table className="tb"><thead><tr><th>Cliente</th><th>Guia</th><th>Tamanho</th></tr></thead><tbody>
          {lista.map((c) => (
            <tr key={c.slug}><td>{c.nome}</td><td>{c.guia_completo ? <span className="st ok">Completo</span> : <span className="st warn">Incompleto</span>}</td><td className="mut">{c.guia_caracteres.toLocaleString("pt-BR")} caracteres</td></tr>
          ))}
        </tbody></table>
        {!lista.length && <p className="vazio">Nenhum cliente encontrado.</p>}
      </div>
    </>
  );
}
