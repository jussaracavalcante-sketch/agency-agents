import "./globals.css";
import Shell from "@/components/Shell";
import MarcaAuth from "@/components/MarcaAuth";
import Link from "next/link";
import { usuarioAtual } from "@/lib/supabase";

export const metadata = { title: "Marketing Ops · Vanguarda Martech" };
export const dynamic = "force-dynamic";

export default async function Layout({ children }: { children: React.ReactNode }) {
  const u = await usuarioAtual();
  return (
    <html lang="pt-BR">
      <body>{u ? <Shell nome={u.nome} papel={u.papel}>{children}</Shell> : <div className="auth"><header className="auth-top"><MarcaAuth /></header><main>{children}</main><footer className="rodape-priv"><Link href="/privacidade">Aviso de privacidade</Link></footer></div>}</body>
    </html>
  );
}
