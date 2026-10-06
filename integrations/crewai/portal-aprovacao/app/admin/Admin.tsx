"use client";
import { useState } from "react";
import type { Ajuste } from "@/lib/admin";

type Perfil = { user_id: string; nome: string; papel: string; portoes: string[] | null; criado_em: string };
type Convite = { email: string; nome: string; cargo: string | null; papel: string; portoes: string[] | null; criado_em: string };
type AgenteCard = { chave: string; papel: string; objetivo: string; tarefas: string[]; ferramentas: string[] };
type Props = {
  eu: string; perfis: Perfil[]; convites: Convite[]; agentes: AgenteCard[]; ajustes: Ajuste[];
  config: { valores: Record<string, string>; descricoes: Record<string, string> };
  plataforma: { item: string; valor: string; nota: string }[];
  pendentes: { chave: string; portao: string | null; cliente: string; desde: string }[]; testes: number;
};
const PAPEIS = ["leitor", "revisor", "aprovador", "admin"];
const PORTOES = ["G1", "G2", "G3"];
const ABAS = [["acessos", "Acessos e papéis"], ["agentes", "Agentes"], ["config", "Custos e ROI"], ["manutencao", "Manutenção"]] as const;

async function chamar(corpo: unknown) {
  const r = await fetch("/api/admin", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, msg: (j.mensagem || j.erro || (r.ok ? "Feito." : "Erro")) as string };
}

export default function Admin(p: Props) {
  const [aba, setAba] = useState<(typeof ABAS)[number][0]>("acessos");
  const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  const [busy, setBusy] = useState(false);
  async function acao(corpo: unknown, confirmar?: string) {
    if (confirmar && !window.confirm(confirmar)) return;
    setBusy(true); const r = await chamar(corpo); setBusy(false); setMsg({ t: r.msg, ok: r.ok });
    if (r.ok) setTimeout(() => window.location.reload(), 1200);
  }
  return (
    <>
      <div className="tabs">{ABAS.map(([k, r]) => <a key={k} href={`#${k}`} className={aba === k ? "on" : ""} onClick={(e) => { e.preventDefault(); setAba(k); setMsg(null); }}>{r}</a>)}</div>
      {msg && <div className={`aviso ${msg.ok ? "" : "err"}`}>{msg.t}</div>}
      {aba === "acessos" && <Acessos p={p} acao={acao} busy={busy} />}
      {aba === "agentes" && <Agentes p={p} acao={acao} busy={busy} />}
      {aba === "config" && <Config p={p} acao={acao} busy={busy} />}
      {aba === "manutencao" && <Manutencao p={p} acao={acao} busy={busy} />}
    </>
  );
}

type Sub = { p: Props; acao: (c: unknown, confirmar?: string) => Promise<void>; busy: boolean };

function Portoes({ valor, onChange }: { valor: string[] | null; onChange: (v: string[] | null) => void }) {
  const sel = valor ?? [];
  return <span style={{ display: "inline-flex", gap: 8 }}>{PORTOES.map((g) => <label key={g} className="chk"><input type="checkbox" checked={sel.includes(g)} onChange={(e) => { const n = e.target.checked ? [...sel, g] : sel.filter((x) => x !== g); onChange(n.length ? n : null); }} />{g}</label>)}<span className="mut" style={{ fontSize: 12 }}>(nenhum marcado = todos)</span></span>;
}

function Acessos({ p, acao, busy }: Sub) {
  const [novo, setNovo] = useState<Convite>({ email: "", nome: "", cargo: "", papel: "revisor", portoes: null, criado_em: "" });
  const [edit, setEdit] = useState<Record<string, { papel: string; portoes: string[] | null }>>({});
  return (
    <>
      <div className="card">
        <h2>Pessoas com acesso ({p.perfis.length})</h2>
        <p className="mut">Papéis: <b>leitor</b> só vê; <b>revisor</b> vê e edita a base de conhecimento; <b>aprovador</b> dispara campanhas e decide portões; <b>admin</b> faz tudo e administra o sistema.</p>
        <table className="tb"><thead><tr><th>Nome</th><th>Papel</th><th>Portões</th><th>Desde</th><th></th></tr></thead><tbody>
          {p.perfis.map((x) => { const e = edit[x.user_id] ?? { papel: x.papel, portoes: x.portoes }; return (
            <tr key={x.user_id}>
              <td>{x.nome}{x.user_id === p.eu && <span className="tag" style={{ marginLeft: 6 }}>você</span>}</td>
              <td><select value={e.papel} onChange={(ev) => setEdit({ ...edit, [x.user_id]: { ...e, papel: ev.target.value } })} style={{ width: 140 }}>{PAPEIS.map((r) => <option key={r}>{r}</option>)}</select></td>
              <td><Portoes valor={e.portoes} onChange={(v) => setEdit({ ...edit, [x.user_id]: { ...e, portoes: v } })} /></td>
              <td className="mut">{new Date(x.criado_em).toLocaleDateString("pt-BR")}</td>
              <td style={{ whiteSpace: "nowrap" }}>
                <button disabled={busy} onClick={() => acao({ acao: "perfil_papel", userId: x.user_id, papel: e.papel, portoes: e.portoes })}>Salvar</button>{" "}
                <button className="d" disabled={busy || x.user_id === p.eu} onClick={() => acao({ acao: "perfil_excluir", userId: x.user_id }, `Remover o acesso de ${x.nome}?`)}>Remover</button>
              </td>
            </tr>); })}
        </tbody></table>
      </div>
      <div className="card">
        <h2>Convites ({p.convites.length})</h2>
        <p className="mut">Quem está convidado entra com o e-mail (link mágico) e recebe o papel no primeiro acesso.</p>
        <table className="tb"><thead><tr><th>E-mail</th><th>Nome</th><th>Cargo</th><th>Papel</th><th>Portões</th><th></th></tr></thead><tbody>
          {p.convites.map((c) => (
            <tr key={c.email}><td>{c.email}</td><td>{c.nome}</td><td className="mut">{c.cargo ?? "—"}</td><td>{c.papel}</td><td>{c.portoes?.join(", ") ?? "todos"}</td>
              <td><button className="d" disabled={busy} onClick={() => acao({ acao: "convite_excluir", email: c.email }, `Excluir o convite de ${c.email}?`)}>Excluir</button></td></tr>
          ))}
          <tr>
            <td><input placeholder="email@empresa.com.br" value={novo.email} onChange={(e) => setNovo({ ...novo, email: e.target.value })} /></td>
            <td><input placeholder="Nome" value={novo.nome} onChange={(e) => setNovo({ ...novo, nome: e.target.value })} /></td>
            <td><input placeholder="Cargo" value={novo.cargo ?? ""} onChange={(e) => setNovo({ ...novo, cargo: e.target.value })} /></td>
            <td><select value={novo.papel} onChange={(e) => setNovo({ ...novo, papel: e.target.value })}>{PAPEIS.map((r) => <option key={r}>{r}</option>)}</select></td>
            <td><Portoes valor={novo.portoes} onChange={(v) => setNovo({ ...novo, portoes: v })} /></td>
            <td><button className="p" disabled={busy} onClick={() => acao({ acao: "convite_salvar", ...novo })}>Convidar</button></td>
          </tr>
        </tbody></table>
      </div>
    </>
  );
}

function Agentes({ p, acao, busy }: Sub) {
  const [estado, setEstado] = useState<Record<string, { ativo: boolean; instrucoes: string }>>(Object.fromEntries(p.ajustes.map((a) => [a.chave, { ativo: a.ativo, instrucoes: a.instrucoes }])));
  return (
    <>
      <div className="card">
        <h2>Manutenção dos agentes</h2>
        <p className="mut">O papel, o objetivo e as ferramentas de cada agente vivem no código da crew (config/agents.yaml) e mudam por deploy. Aqui o administrador escreve <b>instruções complementares por agente</b>, que entram no contexto de toda campanha disparada pelo portal, na seção <code>[AJUSTES DO ADMINISTRADOR]</code>. Elas não liberam dado sem fonte nem removem [VALIDAR]: as travas continuam valendo.</p>
      </div>
      <div className="agrid">
        {p.agentes.map((a) => { const e = estado[a.chave]; const orig = p.ajustes.find((x) => x.chave === a.chave); return (
          <div key={a.chave} className="card">
            <div className="row" style={{ marginBottom: 6 }}><strong>{a.papel}</strong><label className="chk"><input type="checkbox" checked={e.ativo} onChange={(ev) => setEstado({ ...estado, [a.chave]: { ...e, ativo: ev.target.checked } })} />ajuste ativo</label></div>
            <p className="mut" style={{ fontSize: 13 }}>{a.tarefas.length} tarefa(s): {a.tarefas.join(", ")}{a.ferramentas.length ? ` · ferramentas: ${a.ferramentas.join(", ")}` : ""}</p>
            <textarea rows={4} maxLength={1200} placeholder="Ex.: nunca propor campanhas de vídeo; citar sempre o telefone oficial do cliente; limitar o artigo a 900 palavras…" value={e.instrucoes} onChange={(ev) => setEstado({ ...estado, [a.chave]: { ...e, instrucoes: ev.target.value } })} />
            <div className="row"><span className="mut" style={{ fontSize: 12 }}>{orig?.atualizado_nome ? `Última alteração: ${orig.atualizado_nome}, ${new Date(orig.atualizado_em!).toLocaleString("pt-BR", { timeZone: "America/Manaus" })}` : "Sem ajuste salvo"} · {e.instrucoes.length}/1200</span>
              <button className="p" disabled={busy} onClick={() => acao({ acao: "agente_salvar", chave: a.chave, ativo: e.ativo, instrucoes: e.instrucoes })}>Salvar</button></div>
          </div>); })}
      </div>
    </>
  );
}

function Config({ p, acao, busy }: Sub) {
  const [v, setV] = useState<Record<string, string>>({ ...p.config.valores });
  const campos = Object.keys(p.config.descricoes);
  return (
    <>
      <div className="card">
        <h2>Custos por token e referência de ROI</h2>
        <p className="mut">Os tokens reais vêm da plataforma (evento de fim da execução). Os preços abaixo convertem tokens em custo; o valor de referência da campanha permite calcular o retorno.</p>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 12 }}>
          {campos.map((k) => <label key={k}>{p.config.descricoes[k] || k}<input value={v[k] ?? ""} onChange={(e) => setV({ ...v, [k]: e.target.value })} placeholder="número, ponto decimal" /></label>)}
        </div>
        <p className="row" style={{ justifyContent: "flex-end" }}><button className="p" disabled={busy} onClick={() => acao({ acao: "config_salvar", valores: v })}>Salvar configuração</button></p>
      </div>
      <div className="card">
        <h2>Estado da plataforma (somente leitura)</h2>
        <p className="mut">Estas chaves ficam nas variáveis de ambiente da CrewAI AMP e da Vercel; mudam por deploy, não pelo portal.</p>
        <table className="tb"><tbody>{p.plataforma.map((x) => <tr key={x.item}><td>{x.item}</td><td><span className="st ok">{x.valor}</span></td><td className="mut">{x.nota}</td></tr>)}</tbody></table>
      </div>
    </>
  );
}

function Manutencao({ p, acao, busy }: Sub) {
  const [motivo, setMotivo] = useState("Encerrada pelo administrador do sistema");
  return (
    <>
      <div className="card">
        <h2>Execuções paradas em portão ({p.pendentes.length})</h2>
        <p className="mut">Encerrar grava uma reprovação administrativa: a execução sai da fila e nada é publicado. A plataforma segue pausada (não há cancelamento remoto).</p>
        {!p.pendentes.length && <p className="vazio">Nenhuma execução pendente.</p>}
        {!!p.pendentes.length && <>
          <label>Motivo registrado<input value={motivo} onChange={(e) => setMotivo(e.target.value)} /></label>
          <table className="tb"><thead><tr><th>Campanha</th><th>Portão</th><th>Desde</th><th></th></tr></thead><tbody>
            {p.pendentes.map((x) => <tr key={x.chave}><td><a href={`/execucao/${x.chave}`}>{x.cliente}</a></td><td>{x.portao ?? "?"}</td><td className="mut">{new Date(x.desde).toLocaleString("pt-BR", { timeZone: "America/Manaus" })}</td>
              <td><button className="d" disabled={busy} onClick={() => acao({ acao: "execucao_encerrar", execucaoId: x.chave, motivo }, `Encerrar a execução ${x.cliente} no portão ${x.portao ?? ""}?`)}>Encerrar</button></td></tr>)}
          </tbody></table></>}
      </div>
      <div className="card">
        <h2>Eventos de teste</h2>
        <p className="mut">{p.testes} evento(s) com kickoff de teste (prefixo <code>teste-</code>) gravados pelo receptor. Eles não aparecem nas telas, mas ocupam a tabela.</p>
        <button className="d" disabled={busy || !p.testes} onClick={() => acao({ acao: "limpar_testes" }, `Remover ${p.testes} evento(s) de teste?`)}>Limpar eventos de teste</button>
      </div>
    </>
  );
}
