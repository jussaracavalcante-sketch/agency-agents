"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { supabaseNavegador } from "@/lib/browser";

export default function DefinirSenha() {
  const [logado, setLogado] = useState<boolean | null>(null);
  const [senha, setSenha] = useState(""); const [conf, setConf] = useState("");
  const [busy, setBusy] = useState(false); const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  useEffect(() => { supabaseNavegador().auth.getUser().then(({ data }) => setLogado(!!data.user)); }, []);
  async function salvar(e: React.FormEvent) {
    e.preventDefault(); setMsg(null);
    if (senha.length < 8) { setMsg({ t: "Use pelo menos 8 caracteres.", ok: false }); return; }
    if (senha !== conf) { setMsg({ t: "As senhas não conferem.", ok: false }); return; }
    setBusy(true);
    const { error } = await supabaseNavegador().auth.updateUser({ password: senha });
    setBusy(false);
    setMsg(error ? { t: "Não foi possível salvar a senha. Peça um novo link em “Esqueci minha senha”.", ok: false } : { t: "Senha salva. Da próxima vez você pode entrar com e-mail e senha.", ok: true });
    if (!error) setTimeout(() => (window.location.href = "/"), 1800);
  }
  return (
    <div className="auth-box">
      <form onSubmit={salvar} className="card auth-card">
        <h1 style={{ fontSize: 28 }}>Definir senha</h1>
        {logado === false && <p className="sub">O link expirou ou você não está conectado. <Link href="/recuperar">Peça um novo link</Link>.</p>}
        {logado !== false && (
          <>
            <p className="sub">Crie uma senha para entrar com e-mail e senha.</p>
            <label htmlFor="n1">Nova senha</label>
            <input id="n1" type="password" autoComplete="new-password" value={senha} onChange={(e) => setSenha(e.target.value)} required minLength={8} />
            <label htmlFor="n2" style={{ marginTop: 14, display: "block" }}>Confirmar senha</label>
            <input id="n2" type="password" autoComplete="new-password" value={conf} onChange={(e) => setConf(e.target.value)} required minLength={8} />
            <button className="p auth-btn" style={{ marginTop: 16 }} type="submit" disabled={busy || logado === null}>Salvar senha</button>
          </>
        )}
        {msg && <p className="msg" role="status" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
      </form>
    </div>
  );
}
