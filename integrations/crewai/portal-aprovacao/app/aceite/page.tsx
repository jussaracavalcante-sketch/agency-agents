import { redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import { pendentesDe, TODOS } from "@/lib/aceite";
import FormAceite from "./FormAceite";

export const dynamic = "force-dynamic";
export const metadata = { title: "Aceite · Marketing Ops" };

export default async function Aceite() {
  const u = await usuarioAtual({ semAceite: true });
  if (!u) redirect("/login");
  const pend = await pendentesDe(u.id);
  if (!pend.length) redirect("/api/aceite/ok");
  const atualizacao = pend.length < TODOS.length;
  return <FormAceite nome={u.nome} atualizacao={atualizacao} documentos={pend.map((d) => ({ chave: d.chave, titulo: d.titulo, versao: d.versao, md: d.md }))} />;
}
