import { createServerClient } from "@supabase/ssr";
import { createClient } from "@supabase/supabase-js";
import { cookies } from "next/headers";

/** Cliente com a sessão do usuário (cookies). Serve só para saber quem está logado. */
export function sessao() {
  const jar = cookies();
  return createServerClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!, {
    cookies: {
      getAll: () => jar.getAll(),
      setAll: (lista: { name: string; value: string; options?: Record<string, unknown> }[]) => {
        try { lista.forEach(({ name, value, options }) => jar.set(name, value, options as never)); } catch { /* componente de servidor */ }
      },
    },
  });
}

/** Cliente de serviço: só no servidor, depois de validar sessão e papel. */
export function admin() {
  return createClient(process.env.NEXT_PUBLIC_SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
    auth: { persistSession: false },
  });
}

export type Papel = "leitor" | "revisor" | "aprovador";
export type Usuario = { id: string; nome: string; papel: Papel; portoes: string[] | null };

export async function usuarioAtual(): Promise<Usuario | null> {
  const { data } = await sessao().auth.getUser();
  const u = data.user;
  if (!u || !u.email) return null;
  const db = admin();
  const { data: perfil } = await db.from("portal_perfis").select("nome,papel,portoes").eq("user_id", u.id).maybeSingle();
  if (perfil) return { id: u.id, nome: perfil.nome, papel: perfil.papel as Papel, portoes: perfil.portoes ?? null };
  // Primeiro acesso: vincula pelo e-mail pré-cadastrado em portal_convites. Sem convite = sem acesso.
  const { data: convite } = await db.from("portal_convites").select("nome,papel,portoes").ilike("email", u.email).maybeSingle();
  if (!convite) return null;
  await db.from("portal_perfis").insert({ user_id: u.id, nome: convite.nome, papel: convite.papel, portoes: convite.portoes });
  return { id: u.id, nome: convite.nome, papel: convite.papel as Papel, portoes: convite.portoes ?? null };
}

/** Aprovador pode decidir o portão? `portoes` nulo = todos. */
export function podeDecidir(u: Usuario, portao: string | null) {
  if (u.papel !== "aprovador") return false;
  if (!u.portoes || !u.portoes.length) return true;
  return !!portao && u.portoes.includes(portao);
}
