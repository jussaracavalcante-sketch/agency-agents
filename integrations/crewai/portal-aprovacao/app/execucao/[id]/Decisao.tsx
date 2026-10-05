"use client";
import { useState } from "react";

type Decisao = "aprovar" | "devolver" | "reprovar";

/** O que cada botão faz, dito antes de enviar. O texto "enviado" é o que a pessoa verá registrado. */
function resumo(d: Decisao, portao: string | null, instrucoes: string) {
  const g = portao ?? "do portão";
  if (d === "aprovar") return {
    titulo: `Aprovar o portão ${g}`,
    efeito: "A execução é retomada e segue para a próxima etapa. Nenhuma correção é enviada.",
    enviado: "Aprovado.",
    aviso: instrucoes.trim() ? "Você escreveu instruções, mas Aprovar NÃO as envia. Para que sejam aplicadas, cancele e use Devolver com ajustes." : null,
  };
  if (d === "devolver") return {
    titulo: `Devolver o portão ${g} com ajustes`,
    efeito: "A etapa de aplicação reescreve as peças com o seu texto e o portão volta a pedir decisão.",
    enviado: instrucoes.trim(),
    aviso: null,
  };
  return {
    titulo: `Reprovar o portão ${g}`,
    efeito: "A execução é encerrada no portal e não será retomada. Nada é enviado à plataforma e não há como desfazer.",
    enviado: "(nada é enviado à plataforma)",
    aviso: instrucoes.trim() ? "Você escreveu instruções: Reprovar as guarda só como justificativa no histórico e NÃO as envia à plataforma, então nada será reescrito. Para pedir correções, cancele e use Devolver com ajustes." : null,
  };
}

export default function Decisao({ execucaoId, portao, podeDecidir }: { execucaoId: string; portao: string | null; podeDecidir: boolean }) {
  const [instrucoes, setInstrucoes] = useState(""); const [busy, setBusy] = useState(false); const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  const [escolha, setEscolha] = useState<Decisao | null>(null); const [ciente, setCiente] = useState(false);
  async function enviar(decisao: Decisao) {
    setBusy(true); setMsg(null);
    const r = await fetch("/api/decisao", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ execucaoId, decisao, instrucoes, ignorarTexto: ciente }) });
    const j = await r.json(); setBusy(false); setEscolha(null); setCiente(false);
    setMsg({ t: j.mensagem || j.erro || "Erro", ok: r.ok });
    if (r.ok) setTimeout(() => window.location.reload(), 1500);
  }
  if (!podeDecidir) return <div className="card"><strong>Decisão</strong><p className="mut">Seu papel não permite decidir. Peça a um aprovador.</p></div>;
  const r = escolha ? resumo(escolha, portao, instrucoes) : null;
  const perdeTexto = !!r?.aviso && escolha !== "devolver";   // texto digitado que a decisão escolhida não envia
  return (
    <div className="card">
      <strong>Decisão do portão {portao ?? ""}</strong>
      <p className="mut">Para devolver, escreva instruções claras. O texto vai literalmente para a execução.</p>
      <textarea rows={7} value={instrucoes} onChange={(e) => setInstrucoes(e.target.value)} disabled={!!escolha} placeholder="Ex.: remover o depoimento do calendário; marcar a paleta como [VALIDAR]…" />
      {!escolha && (
        <p className="row" style={{ justifyContent: "flex-start" }}>
          <button className="p" disabled={busy || !!instrucoes.trim()} title={instrucoes.trim() ? "Há texto escrito: use Devolver com ajustes, ou apague o texto para aprovar" : undefined} onClick={() => setEscolha("aprovar")}>Aprovar</button>
          <button disabled={busy || !instrucoes.trim()} onClick={() => setEscolha("devolver")}>Devolver com ajustes</button>
          <button className="d" disabled={busy} onClick={() => setEscolha("reprovar")}>Reprovar</button>
        </p>
      )}
      {escolha && r && (
        <div role="alertdialog" aria-label="Confirmar decisão" style={{ border: `2px solid ${escolha === "reprovar" ? "var(--err)" : "var(--ac)"}`, borderRadius: 10, padding: 12, margin: "10px 0" }}>
          <strong>{r.titulo}</strong>
          <p>{r.efeito}</p>
          <p className="mut">Texto que será enviado:</p>
          <pre className="doc" style={{ maxHeight: 160, overflow: "auto" }}>{r.enviado}</pre>
          {r.aviso && <p style={{ color: "var(--err)" }}>⚠ {r.aviso}</p>}
          {perdeTexto && <label style={{ display: "block", margin: "6px 0" }}><input type="checkbox" checked={ciente} onChange={(e) => setCiente(e.target.checked)} /> Entendi: meu texto NÃO será enviado à plataforma</label>}
          <p className="row" style={{ justifyContent: "flex-start" }}>
            <button className={escolha === "reprovar" ? "d" : "p"} disabled={busy || (perdeTexto && !ciente)} onClick={() => enviar(escolha)}>Confirmar: {escolha === "aprovar" ? "Aprovar" : escolha === "devolver" ? "Devolver com ajustes" : "Reprovar"}</button>
            <button disabled={busy} onClick={() => { setEscolha(null); setCiente(false); }}>Cancelar</button>
          </p>
        </div>
      )}
      {!!instrucoes.trim() && <p style={{ color: "var(--err)" }}>Há texto escrito: Aprovar fica bloqueado para o texto não se perder. Use <strong>Devolver com ajustes</strong> para enviá-lo ou apague-o para aprovar.</p>}
      <p className="mut">“Aprovar” libera o portão sem correções. Se você quer que algo seja corrigido, devolva. “Reprovar” encerra a execução.</p>
      {msg && <p className="msg" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
    </div>
  );
}
