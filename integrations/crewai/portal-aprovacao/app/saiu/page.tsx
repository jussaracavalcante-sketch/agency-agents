import Link from "next/link";

export const metadata = { title: "Você saiu · Marketing Ops" };

export default function Saiu() {
  return (
    <div className="auth-box">
      <div className="card auth-card" style={{ textAlign: "center" }}>
        <span className="kic" style={{ background: "var(--ok-bg)", color: "var(--ok)", margin: "8px auto 16px", width: 72, height: 72, fontSize: 34 }}>✔</span>
        <h1 style={{ fontSize: 28 }}>Você saiu da sua conta</h1>
        <p className="sub">Sua sessão foi encerrada.<br />Faça login para acessar o painel novamente.</p>
        <Link className="btn p auth-btn" href="/login">Entrar novamente</Link>
        <p style={{ marginTop: 16 }}><Link href="/login?outra=1">Entrar com outra conta</Link></p>
      </div>
    </div>
  );
}
