"use client";
import { useState } from "react";
import Link from "next/link";
import { supabaseNavegador } from "@/lib/browser";

type Msg = { t: string; ok: boolean } | null;

export default function FormLogin({ semAcesso, google, suporte }: { semAcesso: string | null; google: boolean; suporte: string }) {
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [ver, setVer] = useState(false);
  const [manter, setManter] = useState(true);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<Msg>(null);

  /** "Manter conectado" desmarcado: a sessão vale só até fechar o navegador (a Shell confere esta marca). */
  function lembrar() {
    try {
      localStorage.setItem("ma_manter", manter ? "1" : "0");
      sessionStorage.setItem("ma_ativa", "1");
    } catch { /* navegação privada: segue o padrão */ }
  }

  async function entrar(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setMsg(null);
    const { error } = await supabaseNavegador().auth.signInWithPassword({ email: email.trim(), password: senha });
    if (error) {
      setBusy(false);
      setMsg({ t: "E-mail ou senha incorretos. Se você sempre entrou por link, use “Receber link de acesso” ou “Esqueci minha senha” para criar uma senha.", ok: false });
      return;
    }
    lembrar();
    window.location.href = "/";
  }

  async function link() {
    if (!email.trim()) { setMsg({ t: "Informe seu e-mail para receber o link.", ok: false }); return; }
    setBusy(true); setMsg(null);
    const { error } = await supabaseNavegador().auth.signInWithOtp({
      email: email.trim(),
      options: { emailRedirectTo: `${window.location.origin}/auth/callback`, shouldCreateUser: true },
    });
    setBusy(false);
    if (!error) lembrar();
    setMsg(error ? { t: "Não foi possível enviar o link. Tente novamente.", ok: false } : { t: "Enviamos um link de acesso para o seu e-mail.", ok: true });
  }

  async function comGoogle() {
    lembrar();
    await supabaseNavegador().auth.signInWithOAuth({ provider: "google", options: { redirectTo: `${window.location.origin}/auth/callback` } });
  }

  return (
    <div className="auth-box">
      {semAcesso && (
        <div className="aviso err">
          <strong>{semAcesso}</strong> ainda não tem acesso ao portal. Peça a um aprovador para cadastrar o seu e-mail.
          <form action="/auth/sair" method="post" style={{ marginTop: 8 }}><button className="n" type="submit">Sair e usar outra conta</button></form>
        </div>
      )}
      <form onSubmit={entrar} className="card auth-card">
        <h1>Bem-vindo de volta</h1>
        <p className="sub">Entre para gerenciar a equipe de agentes de marketing.</p>
        {google && (
          <>
            <button type="button" className="n auth-google" onClick={comGoogle} disabled={busy}>
              <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden="true"><path fill="#EA4335" d="M24 9.5c3.5 0 6.6 1.2 9.1 3.6l6.8-6.8C35.8 2.4 30.3 0 24 0 14.6 0 6.5 5.4 2.6 13.2l7.9 6.1C12.4 13.6 17.7 9.5 24 9.5z"/><path fill="#4285F4" d="M46.1 24.5c0-1.6-.1-3.1-.4-4.5H24v9h12.4c-.5 2.9-2.2 5.3-4.6 6.9l7.4 5.7c4.3-4 6.9-9.9 6.9-17.1z"/><path fill="#FBBC05" d="M10.5 28.7c-.5-1.4-.8-3-.8-4.7s.3-3.2.8-4.7l-7.9-6.1C.9 16.4 0 20.1 0 24s.9 7.6 2.6 10.8l7.9-6.1z"/><path fill="#34A853" d="M24 48c6.3 0 11.6-2.1 15.5-5.7l-7.4-5.7c-2.1 1.4-4.8 2.3-8.1 2.3-6.3 0-11.6-4.1-13.5-9.8l-7.9 6.1C6.5 42.6 14.6 48 24 48z"/></svg>
              Continuar com Google
            </button>
            <div className="auth-ou"><span>ou entre com e-mail</span></div>
          </>
        )}
        <label htmlFor="email">E-mail</label>
        <input id="email" type="email" autoComplete="username" placeholder="voce@empresa.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <label htmlFor="senha" style={{ marginTop: 14, display: "block" }}>Senha</label>
        <div className="senha">
          <input id="senha" type={ver ? "text" : "password"} autoComplete="current-password" placeholder="Digite sua senha" value={senha} onChange={(e) => setSenha(e.target.value)} />
          <button type="button" className="olho" aria-label={ver ? "Ocultar senha" : "Mostrar senha"} onClick={() => setVer(!ver)}>{ver ? "🙈" : "👁"}</button>
        </div>
        <div className="row" style={{ margin: "14px 0" }}>
          <label className="chk"><input type="checkbox" checked={manter} onChange={(e) => setManter(e.target.checked)} /> Manter conectado</label>
          <Link href="/recuperar">Esqueci minha senha</Link>
        </div>
        <button className="p auth-btn" type="submit" disabled={busy || !email.trim() || !senha}>Entrar</button>
        <button type="button" className="n auth-btn" style={{ marginTop: 10 }} onClick={link} disabled={busy}>Receber link de acesso por e-mail</button>
        {msg && <p className="msg" role="status" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
        <p className="mut" style={{ textAlign: "center", marginTop: 16 }}>Acesso restrito à equipe. Ainda não tem acesso? Peça um convite a um aprovador.</p>
      </form>
      {suporte && <p className="mut" style={{ textAlign: "center" }}>Precisa de ajuda? <a href={`mailto:${suporte}`}>Fale com o suporte</a></p>}
    </div>
  );
}
