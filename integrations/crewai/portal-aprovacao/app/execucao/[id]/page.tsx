import { notFound, redirect } from "next/navigation";
import { usuarioAtual, admin, podeDecidir } from "@/lib/supabase";
import { obterExecucao } from "@/lib/execucoes";
import Decisao from "./Decisao";

export const dynamic = "force-dynamic";

export default async function Revisao({ params }: { params: { id: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const exec = await obterExecucao(params.id);
  if (!exec) notFound();
  const { data: decisoes } = await admin().from("portal_decisoes").select("*").eq("execucao_id", exec.chave).order("criado_em");
  const tarefas = exec.eventos.filter((e) => e.tipo === "task");
  return (
    <>
      <h2>Execução {exec.chave.slice(0, 8)} {exec.pendente && <span className="tag pend">portão {exec.portao} pendente</span>}</h2>
      <div className="grid">
        <div>
          {exec.pendente && (
            <div className="card">
              <strong>Pedido de aprovação ({exec.portao})</strong>
              <pre className="doc">{exec.pendente.output}</pre>
            </div>
          )}
          <h3>Entregas geradas ({tarefas.length})</h3>
          {tarefas.slice().reverse().map((e) => (
            <details key={e.id} className="card">
              <summary>{e.task_name}</summary>
              <pre className="doc">{e.output}</pre>
            </details>
          ))}
        </div>
        <div>
          {exec.pendente && <Decisao execucaoId={exec.chave} portao={exec.portao} podeDecidir={podeDecidir(u, exec.portao)} />}
          <div className="card">
            <strong>Histórico de decisões</strong>
            {!decisoes?.length && <p className="mut">Nenhuma decisão registrada.</p>}
            {decisoes?.map((d) => (
              <p key={d.id} className="mut">
                {new Date(d.criado_em).toLocaleString("pt-BR", { timeZone: "America/Manaus" })} · {d.portao} · <strong>{d.decisao}</strong> por {d.humano_nome}
                {d.instrucoes ? <><br />“{d.instrucoes}”</> : null}
                {!d.enviado_ao_crewai && d.decisao !== "reprovar" ? <><br /><span style={{ color: "var(--err)" }}>não enviada à plataforma</span></> : null}
              </p>
            ))}
          </div>
        </div>
      </div>
    </>
  );
}
