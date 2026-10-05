import { redirect } from "next/navigation";
import { sessao, usuarioAtual } from "@/lib/supabase";
import FormLogin from "./FormLogin";

export const dynamic = "force-dynamic";

export default async function Login({ searchParams }: { searchParams: { outra?: string } }) {
  const u = await usuarioAtual();
  if (u && !searchParams.outra) redirect("/");
  // Sessão válida, mas e-mail sem convite: explica em vez de ficar voltando para o login.
  const { data } = await sessao().auth.getUser();
  const semAcesso = !u && data.user?.email ? data.user.email : null;
  return <FormLogin semAcesso={semAcesso} google={process.env.NEXT_PUBLIC_LOGIN_GOOGLE === "true"} suporte={process.env.NEXT_PUBLIC_SUPORTE_EMAIL || ""} />;
}
