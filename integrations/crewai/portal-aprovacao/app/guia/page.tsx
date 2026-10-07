import { redirect } from "next/navigation";
import Markdown from "@/components/Markdown";
import { usuarioAtual } from "@/lib/supabase";
import { GUIA } from "@/lib/documentos";

export const dynamic = "force-dynamic";
export const metadata = { title: "Guia de uso · Marketing Ops" };

export default async function Guia() {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  return (
    <div className="doc">
      <article className="card doc-corpo"><Markdown texto={GUIA.md} /></article>
    </div>
  );
}
