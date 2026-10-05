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
  const [{ data }, clientes, { data: decisoes }] = await Promise.all([
    admin().from("crewai_webhook_events").select("id,tipo,task_name,kickoff_id,recebido_em,payload").in("tipo", ["task", "human_input"]).not("kickoff_id", "like", "teste-%").order("id", { ascending: false }).limit(80),
    clientePorExecucao(),
    admin().from("portal_decisoes").select("execucao_id,portao,decisao,criado_em").order("criado_em", { ascending: true }).limit(500),
  ]);
  // Cada pausa vira "respondida" pela primeira decisão da mesma execução posterior a ela; sem decisão depois, continua aguardando.
  const respostaDe = (exec: string, desde: string) => (decisoes || []).find((d) => d.execucao_id === exec && new Date(d.criado_em).getTime() > new Date(desde).getTime());
  const rotuloDecisao: Record<string, [string, string]> = { aprovar: ["ok", "Aprovado"], devolver: ["warn", "Devolvido com ajustes"], reprovar: ["err", "Reprovado"] };
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
                <td>{pausa ? (() => {
                  const r = respostaDe(exec, e.recebido_em);
                  const [cls, texto] = r ? (rotuloDecisao[r.decisao] ?? ["ok", "Respondido"]) : ["warn", "Aguardando aprovação"];
                  return <span className={`st ${cls}`}>{r ? `${r.portao ?? ""} ${texto}`.trim() : texto}</span>;
                })() : <span className="st ok">Concluída</span>}</td>
                <td>{fmt(e.recebido_em)}</td>
              </tr>
            );
          })}
        </tbody></table>
      </div>
    </>
  );
}
