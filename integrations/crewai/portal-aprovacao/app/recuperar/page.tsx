"use client";
import { useState } from "react";
import Link from "next/link";
import { supabaseNavegador } from "@/lib/browser";

export default function Recuperar() {
  const [email, setEmail] = useState(""); const [busy, setBusy] = useState(false); const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null);
  async function enviar(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setMsg(null);
    await supabaseNavegador().auth.resetPasswordForEmail(email.trim(), { redirectTo: `${window.location.origin}/auth/callback?next=/definir-senha` });
    setBusy(false);
    // Mesma resposta para qualquer e-mail: não revela quem tem conta.
    setMsg({ t: "Se o e-mail estiver cadastrado, enviamos um link para definir uma nova senha.", ok: true });
  }
  return (
    <div className="auth-box">
      <form onSubmit={enviar} className="card auth-card">
        <h1 style={{ fontSize: 28 }}>Esqueci minha senha</h1>
        <p className="sub">Informe seu e-mail. Enviaremos um link para criar ou redefinir a senha.</p>
        <label htmlFor="email">E-mail</label>
        <input id="email" type="email" autoComplete="username" placeholder="voce@empresa.com" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <button className="p auth-btn" style={{ marginTop: 16 }} type="submit" disabled={busy || !email.trim()}>Enviar link</button>
        {msg && <p className="msg" role="status" style={{ color: "var(--ok)" }}>{msg.t}</p>}
        <p style={{ textAlign: "center", marginTop: 16 }}><Link href="/login">Voltar ao login</Link></p>
      </form>
    </div>
  );
}
