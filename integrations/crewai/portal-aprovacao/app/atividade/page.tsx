import Link from "next/link";
import { redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import { admin } from "@/lib/supabase";
import { TAREFAS, rotuloTarefa } from "@/lib/agentes";
import { clientePorExecucao, fmt } from "@/lib/dados";

export const dynamic = "force-dynamic";

export default async function Atividade() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const [{ data }, clientes] = await Promise.all([
    admin().from("crewai_webhook_events").select("id,tipo,task_name,kickoff_id,recebido_em,payload").in("tipo", ["task", "human_input"]).not("kickoff_id", "like", "teste-%").order("id", { ascending: false }).limit(80),
    clientePorExecucao(),
  ]);
  return (
    <>
      <div className="head"><div><h1>Atividade</h1><p className="sub" style={{ margin: 0 }}>Últimas 80 entregas e pausas de portão, na ordem em que chegaram.</p></div></div>
      <div className="card">
        <table className="tb"><thead><tr><th>Tarefa</th><th>Agente</th><th>Campanha</th><th>Status</th><th>Horário</th></tr></thead><tbody>
          {(data || []).map((e) => {
            const exec = e.payload?.execution_id || e.kickoff_id;
            const pausa = e.tipo === "human_input";
            return (
              <tr key={e.id}>
                <td>{pausa ? "Pedido de aprovação" : rotuloTarefa(e.task_name || "")}</td>
                <td>{pausa ? "Equipe humana" : TAREFAS[e.task_name || ""]?.papel ?? "agente"}</td>
                <td><Link href={`/execucao/${exec}`}>{clientes.get(exec) || exec.slice(0, 8)}</Link></td>
                <td>{pausa ? <span className="st warn">Aguardando aprovação</span> : <span className="st ok">Concluída</span>}</td>
                <td>{fmt(e.recebido_em)}</td>
              </tr>
            );
          })}
        </tbody></table>
      </div>
    </>
  );
}
