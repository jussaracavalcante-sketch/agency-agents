import Link from "next/link";
import { redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import { AGENTES, TAREFAS, TOTAL_TAREFAS } from "@/lib/agentes";
import { entregasRecentes, haQuanto } from "@/lib/dados";

export const dynamic = "force-dynamic";

export default async function Agentes() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const ent = await entregasRecentes(2000);
  const at = new Map<string, { n: number; ultimo: string }>();
  for (const e of ent) {
    const ag = TAREFAS[e.task_name || ""]?.agente;
    if (!ag) continue;
    const a = at.get(ag);
    at.set(ag, { n: (a?.n ?? 0) + 1, ultimo: a?.ultimo ?? e.recebido_em });
  }
  return (
    <>
      <div className="head"><div><h1>Agentes</h1><p className="sub" style={{ margin: 0 }}>Equipe de {AGENTES.length} agentes e {TOTAL_TAREFAS} tarefas, com aprovação humana nos portões G1, G2 e G3.</p></div></div>
      <div className="agrid">
        {AGENTES.map((a) => {
          const x = at.get(a.chave);
          return (
            <Link key={a.chave} href={`/agentes/${a.chave}`} className="card" style={{ color: "var(--tx)" }}>
              <div className="row" style={{ marginBottom: 8 }}>
                <span className="bola">{a.papel.split(/\s+/).filter((w) => w.length > 2).slice(0, 2).map((w) => w[0]).join("").toUpperCase()}</span>
                <span className="st ok">Ativo</span>
              </div>
              <strong>{a.papel}</strong>
              <p className="mut" style={{ display: "-webkit-box", WebkitLineClamp: 3, WebkitBoxOrient: "vertical", overflow: "hidden" }}>{a.objetivo}</p>
              <div className="mut">{a.tarefas.length} tarefa(s) · {a.ferramentas.length ? `${a.ferramentas.length} ferramenta(s)` : "sem ferramentas"}</div>
              <div className="mut">{x ? `${x.n} entregas · última ${haQuanto(x.ultimo)}` : "sem entregas registradas"}</div>
            </Link>
          );
        })}
      </div>
    </>
  );
}
