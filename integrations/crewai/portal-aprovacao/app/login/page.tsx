"use client";
import { useState } from "react";
import { supabaseNavegador } from "@/lib/browser";

export default function Login() {
  const [email, setEmail] = useState(""); const [senha, setSenha] = useState(""); const [msg, setMsg] = useState("");
  async function entrar(e: React.FormEvent) {
    e.preventDefault(); setMsg("");
    const { error } = await supabaseNavegador().auth.signInWithPassword({ email, password: senha });
    if (error) setMsg("E-mail ou senha inválidos."); else window.location.href = "/";
  }
  return (
    <form onSubmit={entrar} className="card" style={{ maxWidth: 380, margin: "60px auto" }}>
      <h2 style={{ marginTop: 0 }}>Entrar</h2>
      <p className="mut">Acesso restrito à equipe. Peça a criação do seu perfil ao administrador.</p>
      <label>E-mail<input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required /></label>
      <label>Senha<input type="password" value={senha} onChange={(e) => setSenha(e.target.value)} required /></label>
      <p><button className="p" type="submit">Entrar</button></p>
      {msg && <p className="msg" style={{ color: "var(--err)" }}>{msg}</p>}
    </form>
  );
}
