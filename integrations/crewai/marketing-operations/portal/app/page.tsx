import Link from "next/link";
import { redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import { listarExecucoes } from "@/lib/execucoes";

export default async function Fila() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const todas = await listarExecucoes();
  const pend = todas.filter((e) => e.pendente);
  const resto = todas.filter((e) => !e.pendente).slice(0, 15);
  const fmt = (s: string) => new Date(s).toLocaleString("pt-BR", { timeZone: "America/Manaus" });
  return (
    <>
      <h2>Aguardando decisão ({pend.length})</h2>
      {pend.length === 0 && <p className="mut">Nenhum portão pendente.</p>}
      {pend.map((e) => (
        <Link key={e.chave} href={`/execucao/${e.chave}`}>
          <div className="card row">
            <div><strong>Portão {e.portao ?? "?"}</strong> <span className="tag pend">pendente</span>
              <div className="mut">execução {e.chave.slice(0, 8)} · aberta {fmt(e.ultimo)}</div></div>
            <span>Revisar →</span>
          </div>
        </Link>
      ))}
      <h2>Recentes</h2>
      {resto.map((e) => (
        <Link key={e.chave} href={`/execucao/${e.chave}`}>
          <div className="card row">
            <div>execução {e.chave.slice(0, 8)} <span className={`tag ${e.concluida ? "ok" : ""}`}>{e.concluida ? "concluída" : "em andamento"}</span>
              <div className="mut">{e.eventos.length} eventos · último {fmt(e.ultimo)}</div></div>
            <span>Ver →</span>
          </div>
        </Link>
      ))}
    </>
  );
}
