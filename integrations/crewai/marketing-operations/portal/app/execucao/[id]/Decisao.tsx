"use client";
import { useState } from "react";

export default function Decisao({ execucaoId, portao, podeDecidir }: { execucaoId: string; portao: string | null; podeDecidir: boolean }) {
  const [instrucoes, setInstrucoes] = useState(""); const [busy, setBusy] = useState(false); const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  async function enviar(decisao: "aprovar" | "devolver" | "reprovar") {
    if (decisao === "reprovar" && !confirm("Reprovar encerra o fluxo desta execução. Confirmar?")) return;
    setBusy(true); setMsg(null);
    const r = await fetch("/api/decisao", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ execucaoId, decisao, instrucoes }) });
    const j = await r.json(); setBusy(false);
    setMsg({ t: j.mensagem || j.erro || "Erro", ok: r.ok });
    if (r.ok) setTimeout(() => window.location.reload(), 1500);
  }
  if (!podeDecidir) return <div className="card"><strong>Decisão</strong><p className="mut">Seu papel não permite decidir. Peça a um aprovador.</p></div>;
  return (
    <div className="card">
      <strong>Decisão do portão {portao ?? ""}</strong>
      <p className="mut">Para devolver, escreva instruções claras. O texto vai literalmente para a execução.</p>
      <textarea rows={7} value={instrucoes} onChange={(e) => setInstrucoes(e.target.value)} placeholder="Ex.: remover o depoimento do calendário; marcar a paleta como [VALIDAR]…" />
      <p className="row" style={{ justifyContent: "flex-start" }}>
        <button className="p" disabled={busy} onClick={() => enviar("aprovar")}>Aprovar</button>
        <button disabled={busy || !instrucoes.trim()} onClick={() => enviar("devolver")}>Devolver com ajustes</button>
        <button className="d" disabled={busy} onClick={() => enviar("reprovar")}>Reprovar</button>
      </p>
      <p className="mut">“Aprovar” libera o portão; o aplicador usa as instruções de devoluções anteriores. Se você quer que algo seja corrigido, devolva primeiro.</p>
      {msg && <p className="msg" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
    </div>
  );
}
