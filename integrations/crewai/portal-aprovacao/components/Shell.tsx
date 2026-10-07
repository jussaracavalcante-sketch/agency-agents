"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import AoVivo from "./AoVivo";
import GuardaSessao from "./GuardaSessao";

const ITENS = [
  { href: "/", rot: "Visão geral", ic: "⌂" },
  { href: "/agentes", rot: "Agentes", ic: "🤖" },
  { href: "/aprovacoes", rot: "Aprovações", ic: "✔" },
  { href: "/atividade", rot: "Atividade", ic: "▤" },
  { href: "/conhecimento", rot: "Conhecimento", ic: "📖" },
  { href: "/disparar", rot: "Disparar campanha", ic: "➤", so: ["aprovador", "admin"] },
  { href: "/roi", rot: "ROI e custos", ic: "◔", so: ["aprovador", "admin"] },
  { href: "/auditoria", rot: "Auditoria", ic: "☰", so: ["aprovador", "admin"] },
  { href: "/admin", rot: "Administração", ic: "⚙", so: ["admin"] },
];
const MIGALHA: Record<string, string> = { privacidade: "Aviso de privacidade", termo: "Termo de conduta", agentes: "Agentes", aprovacoes: "Aprovações", execucao: "Aprovações", atividade: "Atividade", conhecimento: "Conhecimento", disparar: "Disparar campanha", roi: "ROI e custos", auditoria: "Auditoria", admin: "Administração" };

export default function Shell({ nome, papel, children }: { nome: string; papel: string; children: React.ReactNode }) {
  const p = usePathname() || "/";
  const ativo = (h: string) => (h === "/" ? p === "/" : p.startsWith(h) || (h === "/aprovacoes" && p.startsWith("/execucao")));
  const seg = p.split("/")[1];
  return (
    <div className="shell">
      <aside className="side">
        <Link href="/" className="brand"><img src="/logo-vanguarda.png" alt="" className="logo" width={36} height={36} /><span>Marketing Ops<small>Vanguarda</small></span></Link>
        <nav className="nav">
          {ITENS.filter((i) => !i.so || i.so.includes(papel)).map((i) => (
            <Link key={i.href} href={i.href} className={ativo(i.href) ? "on" : ""}><span className="ic">{i.ic}</span>{i.rot}</Link>
          ))}
        </nav>
        <div className="sp" />
        <div className="eu">
          <span className="av">{nome.split(/\s+/).slice(0, 2).map((x) => x[0]).join("").toUpperCase()}</span>
          <div style={{ flex: 1, minWidth: 0 }}><div style={{ fontWeight: 500 }}>{nome}</div><div className="mut">{papel} · <Link href="/definir-senha">senha</Link> · <Link href="/privacidade">privacidade</Link> · <Link href="/termo">conduta</Link></div></div>
          <form action="/auth/sair" method="post"><button type="submit" className="n sair" title="Sair da conta" aria-label="Sair da conta">⏻</button></form>
        </div>
        <GuardaSessao />
      </aside>
      <div>
        <div className="top">
          <div className="crumb">Vanguarda Martech › <b>{seg ? MIGALHA[seg] ?? seg : "Visão geral"}</b></div>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}><AoVivo /><span className="chipv">Equipe de marketing</span></div>
        </div>
        <div className="content">{children}</div>
      </div>
    </div>
  );
}
