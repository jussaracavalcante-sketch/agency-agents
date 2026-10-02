"use client";
import { useState } from "react";
import { supabaseNavegador } from "@/lib/browser";

export default function Login() {
  const [email, setEmail] = useState(""); const [msg, setMsg] = useState<{ t: string; ok: boolean } | null>(null); const [busy, setBusy] = useState(false);
  async function entrar(e: React.FormEvent) {
    e.preventDefault(); setBusy(true); setMsg(null);
    const { error } = await supabaseNavegador().auth.signInWithOtp({
      email,
      options: { emailRedirectTo: `${window.location.origin}/auth/callback`, shouldCreateUser: true },
    });
    setBusy(false);
    setMsg(error ? { t: "Não foi possível enviar o link. Tente novamente.", ok: false } : { t: "Enviamos um link de acesso para o seu e-mail.", ok: true });
  }
  return (
    <form onSubmit={entrar} className="card" style={{ maxWidth: 400, margin: "60px auto" }}>
      <h2 style={{ marginTop: 0 }}>Entrar no Marketing Ops</h2>
      <p className="mut">Acesso restrito à equipe. Informe seu e-mail corporativo e use o link que chegar na caixa de entrada.</p>
      <label>E-mail<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      <p><button className="p" type="submit" disabled={busy}>Receber link de acesso</button></p>
      {msg && <p className="msg" style={{ color: msg.ok ? "var(--ok)" : "var(--err)" }}>{msg.t}</p>}
    </form>
  );
}
