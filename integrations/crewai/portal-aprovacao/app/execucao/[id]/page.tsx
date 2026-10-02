import { notFound, redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import { obterExecucao } from "@/lib/execucoes";
import PainelAprovacoes from "@/components/PainelAprovacoes";

export const dynamic = "force-dynamic";

export default async function Revisao({ params }: { params: { id: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const exec = await obterExecucao(params.id);
  if (!exec) notFound();
  const aba = exec.pendente ? "aguardando" : exec.concluida ? "concluidas" : "andamento";
  return <PainelAprovacoes u={u} selecionada={exec.chave} aba={aba} />;
}
