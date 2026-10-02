import "./globals.css";
import Shell from "@/components/Shell";
import { usuarioAtual } from "@/lib/supabase";

export const metadata = { title: "Marketing Ops · Vanguarda Martech" };
export const dynamic = "force-dynamic";

export default async function Layout({ children }: { children: React.ReactNode }) {
  const u = await usuarioAtual();
  return (
    <html lang="pt-BR">
      <body>{u ? <Shell nome={u.nome} papel={u.papel}>{children}</Shell> : <main style={{ maxWidth: 480, margin: "0 auto", padding: "0 16px" }}>{children}</main>}</body>
    </html>
  );
}
