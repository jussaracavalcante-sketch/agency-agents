import Link from "next/link";
import { admin, podeDecidir, type Usuario } from "@/lib/supabase";
import { listarExecucoes, obterExecucao } from "@/lib/execucoes";
import { TAREFAS, TOTAL_TAREFAS, rotuloTarefa } from "@/lib/agentes";
import { clientePorExecucao, fmt, haQuanto, hora } from "@/lib/dados";
import Decisao from "@/app/execucao/[id]/Decisao";

type Aba = "aguardando" | "andamento" | "concluidas";

/** Fila de aprovações em três painéis: lista, conteúdo do portão e decisão com contexto. */
export default async function PainelAprovacoes({ u, selecionada, aba }: { u: Usuario; selecionada: string | null; aba: Aba }) {
  const [todas, clientes] = await Promise.all([listarExecucoes(), clientePorExecucao()]);
  const grupos = {
    aguardando: todas.filter((e) => e.pendente),
    andamento: todas.filter((e) => !e.concluida && !e.pendente),
    concluidas: todas.filter((e) => e.concluida),
  };
  const nome = (k: string) => clientes.get(k) || `Execução ${k.slice(0, 8)}`;
  const lista = grupos[aba].slice(0, 30);
  const exec = selecionada ? await obterExecucao(selecionada) : lista[0] ? await obterExecucao(lista[0].chave) : null;
  const { data: decisoes } = exec ? await admin().from("portal_decisoes").select("*").eq("execucao_id", exec.chave).order("criado_em") : { data: [] };
  const tarefas = exec ? exec.eventos.filter((e) => e.tipo === "task") : [];
  const feitas = new Set(tarefas.map((e) => e.task_name)).size;
  const abas: [Aba, string][] = [["aguardando", "Aguardando"], ["andamento", "Em andamento"], ["concluidas", "Concluídas"]];

  return (
    <>
      <div className="head"><div><h1>Aprovações</h1><p className="sub" style={{ margin: 0 }}>Revise o que os agentes produziram e decida nos portões.</p></div></div>
      <div className="fila">
        <div className="card lst">
          <div className="chips">
            {abas.map(([k, r]) => <Link key={k} href={`/aprovacoes?aba=${k}`} className={aba === k ? "on" : ""}>{r} {grupos[k].length}</Link>)}
          </div>
          {!lista.length && <p className="vazio">Nenhuma execução nesta aba.</p>}
          {lista.map((e) => (
            <Link key={e.chave} href={`/execucao/${e.chave}`} className={`it ${exec?.chave === e.chave ? "on" : ""}`}>
              <div className="row" style={{ flexWrap: "nowrap" }}>
                <div className="item" style={{ padding: 0, border: 0 }}>
                  <span className={`bola ${e.pendente ? "w" : e.concluida ? "o" : ""}`}>{e.portao ?? (e.concluida ? "✔" : "…")}</span>
                  <div className="grow"><strong>{nome(e.chave)}</strong><div className="mut">{e.pendente ? `Portão ${e.portao ?? "?"} pendente` : e.concluida ? "Concluída" : "Em andamento"}</div></div>
                </div>
                <span className="mut" style={{ whiteSpace: "nowrap" }}>{haQuanto(e.ultimo)}</span>
              </div>
            </Link>
          ))}
        </div>

        {!exec ? <div className="card"><p className="vazio">Selecione uma execução.</p></div> : (
          <>
            <div>
              <div className="card">
                <div className="row">
                  <h2 style={{ margin: 0 }}>{nome(exec.chave)}</h2>
                  {exec.pendente ? <span className="st warn">Portão {exec.portao ?? "?"} aguardando decisão</span> : exec.concluida ? <span className="st ok">Concluída</span> : <span className="st ac">Em andamento</span>}
                </div>
                <p className="mut">Execução {exec.chave.slice(0, 8)} · {feitas} de {TOTAL_TAREFAS} tarefas entregues · última atividade {fmt(exec.ultimo)}</p>
                {exec.pendente && (<><h3>Pedido de aprovação ({exec.portao})</h3><pre className="doc">{exec.pendente.output}</pre></>)}
              </div>
              <div className="card">
                <h2>Entregas geradas</h2>
                {!tarefas.length && <p className="vazio">Nenhuma entrega ainda.</p>}
                {tarefas.slice().reverse().map((e) => (
                  <details key={e.id}>
                    <summary>{TAREFAS[e.task_name || ""]?.ordem ? `${TAREFAS[e.task_name!].ordem}. ` : ""}{rotuloTarefa(e.task_name || "")}
                      <span className="mut" style={{ fontWeight: 400 }}> · {TAREFAS[e.task_name || ""]?.papel ?? "agente"} · {hora(e.recebido_em)}</span></summary>
                    <pre className="doc">{e.output}</pre>
                  </details>
                ))}
              </div>
            </div>
            <div>
              {exec.pendente && <Decisao execucaoId={exec.chave} portao={exec.portao} podeDecidir={podeDecidir(u, exec.portao)} />}
              <div className="card">
                <h2>Contexto</h2>
                <div className="kv"><span>Cliente</span><span>{clientes.get(exec.chave) || "não informado (execução fora do portal)"}</span></div>
                <div className="kv"><span>Início</span><span>{fmt(exec.inicio)}</span></div>
                <div className="kv"><span>Portão</span><span>{exec.portao ?? "—"}</span></div>
                <div className="kv"><span>Progresso</span><span>{feitas} / {TOTAL_TAREFAS} tarefas</span></div>
              </div>
              <div className="card">
                <h2>Histórico de decisões</h2>
                {!decisoes?.length && <p className="mut">Nenhuma decisão registrada.</p>}
                {decisoes?.map((d) => (
                  <p key={d.id} className="mut">
                    {fmt(d.criado_em)} · {d.portao} · <strong>{d.decisao}</strong> por {d.humano_nome}
                    {d.instrucoes ? <><br />“{d.instrucoes}”</> : null}
                    {!d.enviado_ao_crewai && d.decisao !== "reprovar" ? <><br /><span style={{ color: "var(--err)" }}>não enviada à plataforma</span></> : null}
                  </p>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </>
  );
}
