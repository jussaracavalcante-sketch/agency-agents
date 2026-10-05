"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Doc } from "@/lib/conhecimento";

type Versao = { id: number; doc_chave: string; versao: number; acao: string; autor_nome: string; criado_em: string };
type Msg = { t: string; ok: boolean } | null;
const ROTULO = { repo: "Original do repositório", base_editada: "Editado no portal", adicionado: "Documento acrescentado" } as const;
const fmt = (s: string) => new Date(s).toLocaleString("pt-BR", { timeZone: "America/Manaus" });

async function chamar(corpo: Record<string, unknown>) {
  const r = await fetch("/api/conhecimento", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(corpo) });
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, t: (j.mensagem || j.erro || "Erro inesperado") as string };
}

function DocCard({ slug, doc, versoes, podeEditar, limiteDoc }: { slug: string; doc: Doc; versoes: Versao[]; podeEditar: boolean; limiteDoc: number }) {
  const router = useRouter();
  const [titulo, setTitulo] = useState(doc.titulo);
  const [texto, setTexto] = useState(doc.conteudo);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>(null);
  const base = doc.chave === "guia_identidade_visual.md";
  const mudou = texto !== doc.conteudo || titulo !== doc.titulo;

  async function agir(corpo: Record<string, unknown>, confirmar?: string) {
    if (confirmar && !confirm(confirmar)) return;
    setBusy(true); setMsg(null);
    const r = await chamar({ slug, chave: doc.chave, ...corpo });
    setBusy(false); setMsg({ t: r.t, ok: r.ok });
    if (r.ok) router.refresh();
  }

  return (
    <div className="card">
      <div className="row">
        <h2 style={{ margin: 0 }}>{doc.titulo}</h2>
        <span>
          <span className={`st ${doc.origem === "repo" ? "" : doc.origem === "base_editada" ? "ac" : "warn"}`}>{ROTULO[doc.origem]}</span>{" "}
          {doc.corte === "parcial" && <span className="st err">cortado no limite</span>}
          {doc.corte === "fora" && <span className="st err">fora do limite</span>}
        </span>
      </div>
      <p className="mut">{doc.chave}{doc.atualizado_nome ? ` · versão ${doc.versao} · ${doc.atualizado_nome}, ${fmt(doc.atualizado_em!)}` : ""}</p>
      {!base && podeEditar && <label>Título<input value={titulo} onChange={(e) => setTitulo(e.target.value)} maxLength={120} /></label>}
      <textarea className="mono" rows={base ? 18 : 12} value={texto} readOnly={!podeEditar} onChange={(e) => setTexto(e.target.value)} aria-label={`Conteúdo de ${doc.titulo}`} />
      <p className="mut">{texto.length.toLocaleString("pt-BR")} de {limiteDoc.toLocaleString("pt-BR")} caracteres</p>
      {podeEditar && (
        <p className="row" style={{ justifyContent: "flex-start" }}>
          <button className="p" disabled={busy || !mudou || !texto.trim()} onClick={() => agir({ acao: "salvar", titulo, conteudo: texto, versao: doc.versao })}>Salvar alterações</button>
          {mudou && <button className="n" disabled={busy} onClick={() => { setTexto(doc.conteudo); setTitulo(doc.titulo); }}>Descartar</button>}
          {base && doc.origem === "base_editada" && <button className="d" disabled={busy} onClick={() => agir({ acao: "restaurar_original" }, "Voltar ao guia original do repositório? A versão atual fica no histórico.")}>Restaurar original</button>}
          {!base && <button className="d" disabled={busy} onClick={() => agir({ acao: "excluir" }, `Excluir “${doc.titulo}”? A versão fica no histórico.`)}>Excluir</button>}
        </p>
      )}
      {msg && <p className="msg" role="status" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
      {versoes.length > 0 && (
        <details>
          <summary>Histórico ({versoes.length})</summary>
          {versoes.slice(0, 10).map((v) => (
            <div key={v.id} className="row" style={{ padding: "6px 0" }}>
              <span className="mut">{v.acao === "original" ? "Original do repositório" : `Versão ${v.versao}`} · {v.acao} · {v.autor_nome} · {fmt(v.criado_em)}</span>
              {podeEditar && <button className="n" disabled={busy} onClick={() => agir({ acao: "restaurar_versao", versaoId: v.id }, "Restaurar esta versão? O texto atual fica no histórico.")}>Restaurar</button>}
            </div>
          ))}
        </details>
      )}
    </div>
  );
}

export default function Editor({ slug, nome, completo, docs, versoes, repoOk, podeEditar, limiteContexto, limiteDoc }:
  { slug: string; nome: string; completo: boolean; docs: Doc[]; versoes: Versao[]; repoOk: boolean; podeEditar: boolean; limiteContexto: number; limiteDoc: number }) {
  const router = useRouter();
  const [novoTitulo, setNovoTitulo] = useState("");
  const [novoTexto, setNovoTexto] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>(null);
  const total = docs.reduce((n, d) => n + d.conteudo.length + 2, 0);

  function arquivo(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0];
    if (!f) return;
    if (!/\.(md|markdown|txt)$/i.test(f.name)) { setMsg({ t: "Envie um arquivo .md ou .txt. Para PDF ou Word, cole o texto no campo.", ok: false }); return; }
    if (f.size > 200_000) { setMsg({ t: "Arquivo grande demais (máximo 200 KB).", ok: false }); return; }
    const leitor = new FileReader();
    leitor.onload = () => { setNovoTexto(String(leitor.result || "")); if (!novoTitulo) setNovoTitulo(f.name.replace(/\.[^.]+$/, "").replace(/[_-]+/g, " ")); setMsg(null); };
    leitor.readAsText(f, "utf-8");
  }

  async function adicionar() {
    setBusy(true); setMsg(null);
    const r = await chamar({ acao: "salvar", slug, titulo: novoTitulo, conteudo: novoTexto });
    setBusy(false); setMsg({ t: r.t, ok: r.ok });
    if (r.ok) { setNovoTitulo(""); setNovoTexto(""); router.refresh(); }
  }

  async function marcar(v: boolean) {
    const r = await chamar({ acao: "completo", slug, completo: v });
    setMsg({ t: r.t, ok: r.ok }); if (r.ok) router.refresh();
  }

  return (
    <>
      {!repoOk && <div className="aviso err">Não foi possível ler o guia original do repositório agora. Você pode editar documentos acrescentados, mas o guia base só aparece quando o repositório estiver acessível.</div>}
      <div className="card">
        <div className="row">
          <div>
            <strong>Texto enviado aos agentes: {total.toLocaleString("pt-BR")} de {limiteContexto.toLocaleString("pt-BR")} caracteres</strong>
            <div className="mut">Cada tarefa da campanha recebe esse texto. O que passar do limite é cortado, então coloque o essencial no início. {total > limiteContexto && <span style={{ color: "var(--err)" }}>Acima do limite: reduza ou reordene.</span>}</div>
          </div>
          <div>
            <span className={`st ${completo ? "ok" : "warn"}`}>{completo ? "Guia completo" : "Guia incompleto"}</span>{" "}
            {podeEditar && <button className="n" onClick={() => marcar(!completo)}>{completo ? "Marcar incompleto" : "Marcar completo"}</button>}
          </div>
        </div>
      </div>
      {docs.map((d) => <DocCard key={d.chave + (d.versao ?? 0)} slug={slug} doc={d} podeEditar={podeEditar} limiteDoc={limiteDoc} versoes={versoes.filter((v) => v.doc_chave === d.chave)} />)}
      {podeEditar && (
        <div className="card">
          <h2>Acrescentar documento</h2>
          <p className="mut">Ofertas, tom de voz, restrições legais, perguntas frequentes. Cole o texto ou envie um arquivo .md ou .txt de {nome}.</p>
          <label>Título<input value={novoTitulo} onChange={(e) => setNovoTitulo(e.target.value)} maxLength={120} placeholder="Ex.: Tom de voz e termos proibidos" /></label>
          <label style={{ display: "block", marginTop: 12 }}>Conteúdo<textarea className="mono" rows={10} value={novoTexto} onChange={(e) => setNovoTexto(e.target.value)} placeholder="Cole o texto aqui…" /></label>
          <p className="row" style={{ justifyContent: "flex-start" }}>
            <input type="file" accept=".md,.markdown,.txt" onChange={arquivo} style={{ width: "auto" }} aria-label="Enviar arquivo" />
            <button className="p" disabled={busy || !novoTitulo.trim() || !novoTexto.trim()} onClick={adicionar}>Acrescentar documento</button>
          </p>
          <p className="mut">{novoTexto.length.toLocaleString("pt-BR")} caracteres</p>
        </div>
      )}
      {msg && <p className="msg" role="status" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
    </>
  );
}
