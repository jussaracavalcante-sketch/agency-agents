"use client";
import { useMemo, useState } from "react";
import { CAMPOS, PILOTO_SANTA_JULIA } from "@/lib/briefing";

type Cliente = { slug: string; nome: string; guia_completo: boolean };

export default function Formulario({ clientes }: { clientes: Cliente[] }) {
  const [slug, setSlug] = useState("");
  const [v, setV] = useState<Record<string, string>>(() => Object.fromEntries(CAMPOS.map((c) => [c.chave, c.padrao ?? ""])));
  const [etapa, setEtapa] = useState<"editar" | "revisar">("editar");
  const [ok, setOk] = useState(false);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  const cliente = useMemo(() => clientes.find((c) => c.slug === slug), [clientes, slug]);
  function carregarPiloto() {
    if (!clientes.some((c) => c.slug === PILOTO_SANTA_JULIA.slug)) { setMsg({ t: "Cliente Hospital Santa Júlia não encontrado no cadastro.", ok: false }); return; }
    setSlug(PILOTO_SANTA_JULIA.slug); setV({ ...v, ...PILOTO_SANTA_JULIA.valores }); setMsg(null);
  }
  const faltando = CAMPOS.filter((c) => !v[c.chave]?.trim()).map((c) => c.rotulo);
  const pronto = !!cliente && faltando.length === 0;

  async function disparar() {
    setBusy(true); setMsg(null);
    const r = await fetch("/api/disparo", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ briefing: { ...v, cliente: cliente?.nome, cliente_slug: slug }, confirmou: ok }) });
    const j = await r.json(); setBusy(false);
    setMsg({ t: j.mensagem || j.erro || "Erro", ok: r.ok });
    if (r.ok) setTimeout(() => (window.location.href = "/"), 2500);
  }

  if (etapa === "revisar" && cliente) {
    return (
      <div className="card">
        <h3 style={{ marginTop: 0 }}>Revisar antes de disparar</h3>
        <p><strong>Cliente:</strong> {cliente.nome} {!cliente.guia_completo && <span className="tag pend">guia de marca incompleto</span>}</p>
        {CAMPOS.map((c) => <p key={c.chave} className="mut"><strong style={{ color: "var(--tx)" }}>{c.rotulo}:</strong> {v[c.chave]}</p>)}
        <p className="card" style={{ background: "var(--bg)" }}>
          <label style={{ display: "flex", gap: 8, alignItems: "flex-start" }}>
            <input type="checkbox" style={{ width: "auto", marginTop: 4 }} checked={ok} onChange={(e) => setOk(e.target.checked)} />
            <span>Entendo que cada campanha consome cerca de <strong>360 mil tokens</strong> do modelo e que nada é publicado: a equipe decide em três portões (G1, G2, G3).</span>
          </label>
        </p>
        <p className="row" style={{ justifyContent: "flex-start" }}>
          <button className="p" disabled={!ok || busy} onClick={disparar}>Disparar campanha</button>
          <button disabled={busy} onClick={() => setEtapa("editar")}>Voltar e editar</button>
        </p>
        {msg && <p className="msg" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
      </div>
    );
  }

  return (
    <form className="card" onSubmit={(e) => { e.preventDefault(); if (pronto) setEtapa("revisar"); }}>
      <p className="row" style={{ justifyContent: "flex-start", marginTop: 0 }}>
        <button type="button" className="n" onClick={carregarPiloto}>Carregar briefing do piloto Santa Júlia</button>
        <span className="mut">Preenche cliente e campos com o briefing validado. Revise antes de disparar.</span>
      </p>
      {msg && !msg.ok && <p className="msg" style={{ color: "var(--err)" }}>{msg.t}</p>}
      <label>Cliente (guia de marca)
        <select value={slug} onChange={(e) => setSlug(e.target.value)} required style={{ width: "100%", padding: 10, borderRadius: 8, border: "1px solid var(--bd)", background: "var(--card)", color: "var(--tx)" }}>
          <option value="">Selecione…</option>
          {clientes.map((c) => <option key={c.slug} value={c.slug}>{c.nome}{c.guia_completo ? "" : " (guia incompleto)"}</option>)}
        </select>
      </label>
      {cliente && !cliente.guia_completo && <p className="mut" style={{ color: "var(--warn)" }}>O guia deste cliente foi truncado na extração: as decisões de marca sairão como [VALIDAR].</p>}
      {CAMPOS.map((c) => (
        <label key={c.chave} style={{ display: "block", marginTop: 12 }}>{c.rotulo}
          {c.longo
            ? <textarea rows={3} value={v[c.chave]} onChange={(e) => setV({ ...v, [c.chave]: e.target.value })} placeholder={c.dica} />
            : <input value={v[c.chave]} onChange={(e) => setV({ ...v, [c.chave]: e.target.value })} placeholder={c.dica} />}
          <span className="mut">{c.dica}</span>
        </label>
      ))}
      <p><button className="p" type="submit" disabled={!pronto}>Revisar disparo</button>
        {!pronto && <span className="mut"> {cliente ? `Falta: ${faltando.join(", ")}` : "Selecione o cliente."}</span>}</p>
    </form>
  );
}
