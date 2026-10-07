"use client";
import { useState } from "react";
import Markdown from "@/components/Markdown";
import AvisoMinuta from "@/components/AvisoMinuta";

type Doc = { chave: string; titulo: string; versao: string; md: string };

export default function FormAceite({ nome, atualizacao, documentos }: { nome: string; atualizacao: boolean; documentos: Doc[] }) {
  const [marcados, setMarcados] = useState<Record<string, boolean>>({});
  const [erro, setErro] = useState("");
  const [enviando, setEnviando] = useState(false);
  const todos = documentos.every((d) => marcados[d.chave]);

  async function enviar() {
    setErro(""); setEnviando(true);
    try {
      const r = await fetch("/api/aceite", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ documentos: documentos.map((d) => d.chave), confirmou: true }) });
      const j = await r.json().catch(() => ({}));
      if (!r.ok) { setErro(j.erro || "Não foi possível registrar o aceite."); setEnviando(false); return; }
      window.location.href = "/";
    } catch { setErro("Falha de conexão. Tente de novo."); setEnviando(false); }
  }

  return (
    <div className="doc">
      <div className="card" style={{ padding: "20px 24px" }}>
        <h1 style={{ fontSize: 24 }}>{atualizacao ? "Atualização de documentos" : "Antes de começar"}</h1>
        <p className="sub">{nome}, para usar o portal leia {documentos.length > 1 ? "os documentos abaixo" : "o documento abaixo"} e confirme. {atualizacao ? "Houve mudança desde o seu último aceite." : "Este registro é feito uma vez e guardado na trilha de auditoria."}</p>
      </div>
      {documentos.map((d) => (
        <section key={d.chave}>
          <AvisoMinuta md={d.md} versao={d.versao} />
          <article className="card doc-corpo doc-rolagem" tabIndex={0} aria-label={d.titulo}><Markdown texto={d.md} /></article>
          <label className="aceite-linha">
            <input type="checkbox" checked={!!marcados[d.chave]} onChange={(e) => setMarcados({ ...marcados, [d.chave]: e.target.checked })} />
            <span>{d.chave === "aviso" ? <>Li e estou ciente do <b>{d.titulo}</b> (versão {d.versao}).</> : <>Li, entendi e aceito o <b>{d.titulo}</b> (versão {d.versao}).</>}</span>
          </label>
        </section>
      ))}
      {erro && <div className="aviso-erro" role="alert">{erro}</div>}
      <div style={{ display: "flex", gap: 12, alignItems: "center", margin: "8px 0 40px" }}>
        <button className="btn p" disabled={!todos || enviando} onClick={enviar}>{enviando ? "Registrando…" : "Confirmar e entrar"}</button>
        <form action="/auth/sair" method="post"><button className="btn" type="submit">Sair sem aceitar</button></form>
      </div>
    </div>
  );
}
