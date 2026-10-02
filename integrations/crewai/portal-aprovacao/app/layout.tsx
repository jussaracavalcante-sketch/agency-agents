import "./globals.css";
import Link from "next/link";
import { usuarioAtual } from "@/lib/supabase";

export const metadata = { title: "Portal de Aprovação · Marketing Ops" };
export const dynamic = "force-dynamic";

export default async function Layout({ children }: { children: React.ReactNode }) {
  const u = await usuarioAtual();
  return (
    <html lang="pt-BR">
      <body>
        <header>
          <Link href="/"><strong>Portal de Aprovação</strong></Link>
          {u && (
            <nav style={{ display: "flex", gap: 16 }}>
              <Link href="/">Fila</Link>
              <Link href="/agentes">Agentes</Link>
              {u.papel === "aprovador" && <Link href="/disparar">Disparar campanha</Link>}
            </nav>
          )}
          <span className="mut">{u ? `${u.nome} · ${u.papel}` : "não autenticado"}</span>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
