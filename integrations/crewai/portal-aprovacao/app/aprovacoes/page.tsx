import { redirect } from "next/navigation";
import { usuarioAtual } from "@/lib/supabase";
import PainelAprovacoes from "@/components/PainelAprovacoes";

export const dynamic = "force-dynamic";

export default async function Aprovacoes({ searchParams }: { searchParams: { aba?: string } }) {
  const u = await usuarioAtual();
  if (!u) redirect("/login");
  const aba = searchParams.aba === "andamento" || searchParams.aba === "concluidas" ? searchParams.aba : "aguardando";
  return <PainelAprovacoes u={u} selecionada={null} aba={aba} />;
}
