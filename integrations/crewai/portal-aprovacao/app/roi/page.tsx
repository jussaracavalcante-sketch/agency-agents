import Link from "next/link";
import { redirect } from "next/navigation";
import { ehAdmin, ehAprovador, usuarioAtual } from "@/lib/supabase";
import { analiseROI } from "@/lib/roi";
import { fmt } from "@/lib/dados";

export const dynamic = "force-dynamic";
const brl = (v: number) => v.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
const usd = (v: number) => v.toLocaleString("pt-BR", { style: "currency", currency: "USD" });
const mil = (v: number) => (v / 1000).toLocaleString("pt-BR", { maximumFractionDigits: 1 }) + " mil";

export default async function ROI() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  if (!ehAdmin(u) && !ehAprovador(u)) return <div className="card"><h1>ROI da plataforma</h1><p className="mut">Seu papel não acessa a análise de custos.</p></div>;
  const a = await analiseROI();
  const p = a.precos;
  const custoPorTarefa = a.totais.tarefas ? a.totais.brl / a.totais.tarefas : 0;
  return (
    <>
      <div className="head">
        <div><h1>ROI e custos da plataforma de agentes</h1><p className="sub" style={{ margin: 0 }}>Tokens reais por execução (evento de fim da crew) convertidos em custo pelos preços configurados. Execução sem evento de fim recebe estimativa marcada.</p></div>
        {ehAdmin(u) && <Link className="btn" href="/admin#config">Ajustar preços</Link>}
      </div>
      <div className="kpis">
        <div className="card"><span className="kic" style={{ background: "var(--vio-bg)", color: "var(--vio)" }}>◔</span><div><div className="kl">Tokens consumidos</div><div className="kn">{mil(a.totais.tokens)}</div><div className="kl">{a.campanhas.length} execução(ões), {a.reais} com token real</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--ac-bg)", color: "var(--ac)" }}>R$</span><div><div className="kl">Custo total</div><div className="kn">{brl(a.totais.brl)}</div><div className="kl">{usd(a.totais.usd)} · câmbio {p.cambio.toLocaleString("pt-BR")}</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--ok-bg)", color: "var(--ok)" }}>÷</span><div><div className="kl">Custo por campanha concluída</div><div className="kn">{a.concluidas ? brl(a.mediaConcluida) : "—"}</div><div className="kl">{a.concluidas} concluída(s) · {brl(custoPorTarefa)} por tarefa</div></div></div>
        <div className="card"><span className="kic" style={{ background: "var(--warn-bg)", color: "var(--warn)" }}>%</span><div><div className="kl">ROI por campanha</div><div className="kn">{a.roi === null ? "—" : `${Math.round(a.roi * 100).toLocaleString("pt-BR")}%`}</div><div className="kl">{p.valorRef ? `valor de referência ${brl(p.valorRef)}` : "defina o valor de referência da campanha na administração"}</div></div></div>
      </div>
      <div className="two">
        <div className="card">
          <h2>Custo por token</h2>
          <table className="tb"><tbody>
            <tr><td>Entrada (prompt)</td><td>US$ {p.entrada} / milhão</td><td className="mut">{brl(p.entrada * p.cambio / 1_000_000)} por token</td></tr>
            <tr><td>Entrada em cache</td><td>US$ {p.cache} / milhão</td><td className="mut">{brl(p.cache * p.cambio / 1_000_000)} por token</td></tr>
            <tr><td>Saída (completion)</td><td>US$ {p.saida} / milhão</td><td className="mut">{brl(p.saida * p.cambio / 1_000_000)} por token</td></tr>
            <tr><td><b>Custo médio efetivo</b></td><td colSpan={2}><b>{(a.custoPorToken * 1_000_000).toLocaleString("pt-BR", { style: "currency", currency: "BRL" })} por milhão de tokens</b> ({a.custoPorToken.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 6 })} por token)</td></tr>
            <tr><td>Tokens por tarefa (observado)</td><td colSpan={2}>{Math.round(a.porTarefa).toLocaleString("pt-BR")}</td></tr>
          </tbody></table>
          {!!a.economiaHoras && <p className="mut">Esforço humano substituído por campanha: {brl(a.economiaHoras)} ({p.horas} h × {brl(p.custoHora)}). Comparado ao custo médio por campanha concluída, a economia é de {brl(a.economiaHoras - a.mediaConcluida)}.</p>}
        </div>
        <div className="card">
          <h2>Custo por agente (rateio pelo tamanho das entregas)</h2>
          <table className="tb"><thead><tr><th>Agente</th><th>Tarefas</th><th>Tokens</th><th>Custo</th></tr></thead><tbody>
            {a.porAgente.map((x) => <tr key={x.agente}><td>{x.agente}</td><td>{x.tarefas}</td><td>{mil(x.tokens)}</td><td>{brl(x.brl)}</td></tr>)}
          </tbody></table>
        </div>
      </div>
      <div className="card">
        <h2>Valor por campanha gerada</h2>
        <table className="tb"><thead><tr><th>Campanha</th><th>Início</th><th>Status</th><th>Tarefas</th><th>Decisões</th><th>Tokens</th><th>Custo</th><th>Base</th></tr></thead><tbody>
          {a.campanhas.map((c) => (
            <tr key={c.chave}>
              <td><Link href={`/execucao/${c.chave}`}>{c.cliente}</Link><div className="mut" style={{ fontSize: 12 }}>{c.chave.slice(0, 8)}</div></td>
              <td className="mut">{fmt(c.inicio)}</td>
              <td><span className={`st ${c.status === "Concluída" ? "ok" : c.status === "Reprovada" ? "err" : "warn"}`}>{c.status}</span></td>
              <td>{c.tarefas}</td><td>{c.decisoes}</td>
              <td>{mil(c.tokens.total_tokens)}<div className="mut" style={{ fontSize: 12 }}>{mil(c.tokens.prompt_tokens)} entrada · {mil(c.tokens.completion_tokens)} saída</div></td>
              <td><b>{brl(c.custo_brl)}</b><div className="mut" style={{ fontSize: 12 }}>{usd(c.custo_usd)}</div></td>
              <td>{c.estimado ? <span className="st warn">estimado</span> : <span className="st ok">real</span>}</td>
            </tr>
          ))}
        </tbody></table>
        <p className="mut" style={{ fontSize: 12 }}>Estimativa: tokens por tarefa observados nas execuções com token real × tarefas entregues. Execuções com várias retomadas somam o token de cada retomada concluída.</p>
      </div>
    </>
  );
}
